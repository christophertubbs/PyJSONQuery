import typing
from lxml import etree
import io
from collections import Counter


def init() -> typing.NoReturn:
    if hasattr(etree, "from_json") and hasattr(etree, "from_json_file"):
        return

    import json
    import collections.abc as abstract_collections

    def _is_slotted(value: typing.Any) -> bool:
        return hasattr(value, "__slots__")

    def _is_collection(value: typing.Any) -> bool:
        return not isinstance(value, str) \
               and not isinstance(value, bytes) \
               and isinstance(value, abstract_collections.Container)

    def _is_basic_value(value: typing.Any) -> bool:
        return not hasattr(value, "__dict__") and not _is_slotted(value) and not _is_collection(value)

    def _build_element(key: str, value: typing.Any) -> typing.Iterable[etree.ElementBase]:
        elements: typing.List[etree.ElementBase] = list()

        if _is_basic_value(value):
            element = etree.Element(key)
            element.set("datatype", type(value).__name__)
            element.set("list_member", str(False))
            element.text = str(value)
            elements.append(element)
        elif isinstance(value, abstract_collections.Mapping):
            element = etree.Element(key)
            element.set("datatype", type(value).__name__)
            element.set("list_member", str(False))
            found_keys = Counter()
            found_nodes = list()
            for sub_key, sub_value in value.items():
                sub_elements = _build_element(sub_key, sub_value)
                for node in sub_elements:
                    found_keys[node.tag] += 1
                    found_nodes.append(node)
            key_indices = Counter()
            for node in found_nodes:
                if found_keys[node.tag] > 1:
                    node.set('list_member', str(True))
                    node.set('index', str(key_indices[node.tag]))
                    key_indices[node.tag] += 1
                element.append(node)
            elements.append(element)
        elif _is_collection(value):
            list_index = 0
            for sub_value in value:
                for element in _build_element(key, sub_value):
                    element.set("list_member", str(True))
                    element.set("index", str(list_index))
                    elements.append(element)
                list_index += 1
        elif hasattr(value, "__dict__"):
            element = etree.Element(key)
            element.set("datatype", type(value).__name__)
            element.set("list_member", str(False))
            for sub_key, sub_value in value.__dict__.items():
                if isinstance(sub_value, typing.Callable):
                    continue
                nodes = _build_element(sub_key, sub_value)

                for node in nodes:
                    element.append(node)

            elements.append(element)
        elif _is_slotted(value):
            keys: typing.Iterable[str] = value.__slots__
            element = etree.Element(key)
            element.set("datatype", type(value).__name__)
            element.set("list_member", str(False))

            for slotted_variable in keys:
                value = getattr(value, slotted_variable)

                if isinstance(value, typing.Callable):
                    continue

                nodes = _build_element(slotted_variable, value)

                for node in nodes:
                    element.append(node)

            elements.append(element)
        else:
            raise ValueError(f"Object of type '{type(value)}' ({str(value)}) cannot be converted to XML.")

        return elements

    def _build_tree(data: typing.Dict[str, typing.Any]) -> etree.ElementBase:
        tree = etree.Element("root")

        for key, value in data.items():
            nodes = _build_element(key, value)
            for node in nodes:
                tree.append(node)

        return tree

    def from_json(data: typing.Union[str, io.IOBase, dict]) -> etree.ElementBase:
        if isinstance(data, io.IOBase):
            data = json.load(data)

        if isinstance(data, str):
            data = json.loads(data)

        return _build_tree(data)

    def from_json_file(path_or_buffer: typing.Union[str, io.IOBase]) -> etree.ElementBase:
        if isinstance(path_or_buffer, str):
            with open(path_or_buffer, 'r') as json_file:
                data = json.load(json_file)
        else:
            data = json.load(path_or_buffer)

        return from_json(data)


    def query_from_json(data: typing.Union[str, io.IOBase, dict], path: str) -> typing.Sequence[etree.ElementBase]:
        tree = etree.from_json(data)
        xpath_results = tree.xpath(path)
        converted_results = _xml_to_json(xpath_results)
        return converted_results


    def query_from_json_file(data: typing.Union[str, io.IOBase], path: str) -> typing.Any:
        tree = etree.from_json_file(data)
        xpath_results = tree.xpath(path)
        converted_results = _xml_to_json(xpath_results)

        if len(converted_results) == 1:
            keys = [key for key in converted_results.keys()]
            converted_results = converted_results[keys[0]]

        return converted_results

    def _xml_to_json(nodes: typing.Sequence[etree.ElementBase]) -> dict:
        results = dict()
        actual_values = dict()

        for node in nodes:
            if node.tag not in actual_values:
                actual_values[node.tag] = node
            else:
                if not isinstance(actual_values[node.tag], list):
                    actual_values[node.tag] = [actual_values[node.tag]]
                actual_values[node.tag].append(node)

        list_nodes = [
            (name, similar_nodes)
            for name, similar_nodes in actual_values.items()
            if isinstance(similar_nodes, list)
        ]

        for name, found_nodes in list_nodes:
            for found_node in found_nodes:
                found_node.set("list_member", str(True))

            actual_values[name] = sorted(actual_values[name], key=lambda n: int(n.getparent().get("index", 0)))

        for tag, value in actual_values.items():
            if isinstance(value, list):
                results[tag] = list()

                for element in value:
                    datatype = element.get("datatype", None)
                    children = element.getchildren()
                    if len(children) > 0:
                        child_results = _xml_to_json(children)
                        results[tag].append(child_results)
                    elif datatype == 'float':
                        results[tag].append(float(element.text))
                    elif datatype == 'int':
                        results[tag].append(float(element.text))
                    else:
                        results[tag].append(element.text)

                continue

            datatype = value.get("database", "str")

            if datatype == 'dict':
                child_nodes = value.getchildren()
                child_results = dict()
                for nested_node in child_nodes:
                    nested_data = _xml_to_json([nested_node])
                    child_results[tag] = nested_data
                results[tag] = child_results
            elif datatype == 'float':
                results[tag] = float(value.text)
            elif datatype == 'int':
                results[tag] = int(value.text)
            else:
                results[tag] = value.text

        if len(results) == 1:
            keys = [key for key in results.keys()]
            results = results[keys[0]]

        return results

    if not hasattr(etree, "from_json"):
        setattr(etree, "from_json", from_json)

    if not hasattr(etree, "from_json_file"):
        setattr(etree, "from_json_file", from_json_file)

    if not hasattr(etree, "query_from_json"):
        setattr(etree, "query_from_json", query_from_json)

    if not hasattr(etree, "query_from_json_file"):
        setattr(etree, "query_from_json_file", query_from_json_file)


init()


def xml_from_json(data: typing.Union[str, io.IOBase, dict]) -> etree.ElementBase:
    return etree.from_json(data)


def xml_from_json_file(path_or_buffer: typing.Union[str, io.IOBase]) -> etree.ElementBase:
    return etree.from_json_file(path_or_buffer)


def query_from_json(data: typing.Union[str, io.IOBase, dict], path: str) -> typing.Sequence[etree.ElementBase]:
    results = etree.query_from_json(data, path)
    return results


def query_from_json_file(data: typing.Union[str, io.IOBase], path: str) -> typing.Any:
    results = etree.query_from_json_file(data, path)
    return results
