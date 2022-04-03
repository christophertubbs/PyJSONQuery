import typing
from lxml import etree
import io


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
            for sub_key, sub_value in value.items():
                for node in _build_element(sub_key, sub_value):
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

    if not hasattr(etree, "from_json"):
        setattr(etree, "from_json", from_json)

    if not hasattr(etree, "from_json_file"):
        setattr(etree, "from_json_file", from_json_file)


init()


def xml_from_json(data: typing.Union[str, io.IOBase, dict]) -> etree.ElementBase:
    return etree.from_json(data)


def xml_from_json_file(path_or_buffer: typing.Union[str, io.IOBase]) -> etree.ElementBase:
    return etree.from_json_file(path_or_buffer)


def query_from_json(data: typing.Union[str, io.IOBase, dict], path: str) -> typing.Sequence[etree.ElementBase]:
    tree = etree.from_json(data)
    return tree.xpath(path)


def query_from_json_file(data: typing.Union[str, io.IOBase], path: str) -> typing.Sequence[etree.ElementBase]:
    tree = etree.from_json_file(data)
    return tree.xpath(path)
