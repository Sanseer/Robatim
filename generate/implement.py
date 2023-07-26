import random
from collections import defaultdict
import json
from typing import Iterator

with open("idioms.json", "r") as f:
    idioms = json.load(f)

_available_colors = idioms["available_colors"]


class SymbolChild:
    def __init__(self, symbol: str, groove_units: int) -> None:
        self._symbol = symbol
        self._groove_units = groove_units
        self.duplicate_id = (0, 0)

    def __str__(self) -> str:
        return self._symbol

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    @property
    def groove_units(self) -> int:
        return self._groove_units


class StructuralNode:
    def __init__(self) -> None:
        self._children: list[SymbolChild] = []
        self.modifier = ""

    def __str__(self) -> str:
        return "-".join(str(child) for child in self._children)

    def __repr__(self) -> str:
        return f"'{self}'"

    def __iter__(self) -> Iterator[SymbolChild]:
        return iter(self._children)


class SymbolParent:
    def __init__(self, symbol: str) -> None:
        self._symbol = symbol
        self._children: list[SymbolChild] = []

    def __str__(self) -> str:
        return self._symbol

    def __iter__(self) -> Iterator[SymbolChild]:
        return iter(self._children)

    @property
    def groove_units(self) -> int:
        return sum(child._groove_units for child in self._children)


class TimeKeeper:
    def __init__(self, template: list[list[str]]) -> None:
        self.structural_nodes: list[StructuralNode] = []
        self.symbol_parents: list[SymbolParent] = []
        self._motif_colors: dict[int, list[int]] = {}
        self.__parse_template(template)
        self.__set_symbol_repeats()

    def __parse_template(self, template: list[list[str]]) -> None:
        previous_symbol = None
        for section in template:
            if len(section) == 1:
                continue
            for positional_item in section:
                structural_node = StructuralNode()
                if "-" in positional_item:
                    groove_units = 1
                else:
                    groove_units = 2
                for current_symbol in positional_item.split("-"):
                    if current_symbol != previous_symbol:
                        symbol_parent = SymbolParent(current_symbol)
                        self.symbol_parents.append(symbol_parent)

                    symbol_child = SymbolChild(current_symbol, groove_units)
                    symbol_parent._children.append(symbol_child)
                    structural_node._children.append(symbol_child)

                    previous_symbol = current_symbol
                self.structural_nodes.append(structural_node)

        node_index = 0
        for section in template:
            if len(section) != 1:
                node_index += len(section)
            else:
                modifier = section[0]
                is_drum_transition = False
                if modifier == "TRANSITION":
                    is_drum_transition = True
                elif modifier == "*TRANSITION" and random.choice((True, False)):
                    is_drum_transition = True

                if is_drum_transition:
                    print(f"Drum fill at index {node_index}!")
                    self.structural_nodes[node_index - 1].modifier = "DRUM_FILL"
                    self.structural_nodes[node_index].modifier = "CYM_CRASH"

    def __set_symbol_repeats(self) -> None:
        SEGMENT_SIZE = 4
        """You can't predict how many symbol children a segment will have.
        Therefore, setting the size of the list ahead of time is not possible"""
        symbol_repeats: dict[str, list[list[SymbolChild]]] = defaultdict(list)
        segment: list[StructuralNode] = []

        for structural_node in self.structural_nodes:
            segment.append(structural_node)
            if len(segment) == SEGMENT_SIZE:
                segment_id = str(segment)
                if segment_id not in symbol_repeats:
                    for current_node in segment:
                        for symbol_child in current_node:
                            symbol_repeats[segment_id].append([symbol_child])
                else:
                    repeat_index = 0
                    for current_node in segment:
                        for symbol_child in current_node:
                            symbol_repeats[segment_id][repeat_index].append(
                                symbol_child
                            )
                            repeat_index += 1
                segment = []

        motif_count = 1
        available_colors = _available_colors[:]
        random.shuffle(available_colors)
        for motif_group in symbol_repeats.values():
            if len(motif_group[0]) == 1:
                continue

            for repeat_index, child_group in enumerate(motif_group):
                for symbol_child in child_group:
                    symbol_child.duplicate_id = (motif_count, repeat_index)

            self._motif_colors[motif_count] = available_colors.pop()
            motif_count += 1

    def __display(self, input_string: str, reference_node: StructuralNode) -> str:
        duplicate_id = reference_node._children[0].duplicate_id
        if duplicate_id == (0, 0):
            return input_string
        color_obj = self._motif_colors[duplicate_id[0]]
        red, green, blue = color_obj
        ansi_color = f"\x1b[38;2;{red};{green};{blue}m"
        return f"{ansi_color}{input_string}\x1b[0m"

    @staticmethod
    def print_colored_list(input_list: list[str]) -> None:
        """Containers like lists and dicts always use the result of
        __repr__ to represent the objects they contain.
        Need manual print to display colors of strings in collection"""
        output = ", ".join(input_list)
        print(f"[{output}]")

    def print_formatted(self) -> None:
        segment = []
        for structural_node in self.structural_nodes:
            segment.append(self.__display(repr(structural_node), structural_node))
            if len(segment) == 8:
                self.print_colored_list(segment)
                segment = []

    @property
    def symbol_sequence(self) -> list[str]:
        return [str(symbol_parent) for symbol_parent in self.symbol_parents]

    @property
    def symbol_parent_repeats(self) -> dict[int, set[int]]:
        symbol_parent_pairings = defaultdict(set)
        for index, symbol_parent in enumerate(self.symbol_parents):
            for symbol_child in symbol_parent:
                duplicate_id = symbol_child.duplicate_id
                if duplicate_id == (0, 0):
                    continue
                symbol_parent_pairings[duplicate_id].add(index)

        result = defaultdict(set)
        for duplicate_group in symbol_parent_pairings.values():
            for primary_index in duplicate_group:
                for secondary_index in duplicate_group:
                    result[primary_index].add(secondary_index)

        return result

    def print_corresponding_sequence(self, input_sequence: list[str]) -> None:
        sequence_iter = iter(input_sequence)
        segment = []
        previous_item = "NULL"
        previous_symbol_child = None

        for structural_node in self.structural_nodes:
            current_items: list[str] = []
            for current_symbol_child in structural_node:
                if current_symbol_child == previous_symbol_child:
                    current_items.append(previous_item)
                else:
                    current_item = next(sequence_iter)
                    current_items.append(current_item)
                    previous_item = current_item
                    previous_symbol_child = current_symbol_child

            composite_item = "-".join(current_items)
            composite_item = self.__display(repr(composite_item), structural_node)
            segment.append(composite_item)

            if len(segment) == 8:
                self.print_colored_list(segment)
                segment = []
