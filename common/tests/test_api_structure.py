"""
Checks the conventions every endpoint follows (see .kiro/steering/code-layout.md), so that new endpoints can't drift
from them.
"""
import re

import pytest
from django.urls import resolve

from cs_cas.api import api
from cs_cas.docs import TAG_GROUPS

SCHEMA = api.get_openapi_schema()
OPERATIONS = [(path, method, operation)
              for path, methods in SCHEMA['paths'].items()
              for method, operation in methods.items()]

# Path parameters that are plain text by nature: Google Places ids.
TEXT_PARAMETERS = {'place_id'}


def test_every_tag_is_grouped_in_the_docs_and_every_group_tag_is_used():
    grouped = {tag for group in TAG_GROUPS for tag in group['tags']}
    used = {tag for _, _, operation in OPERATIONS for tag in operation.get('tags', [])}

    assert used - grouped == set(), 'add these tags to TAG_GROUPS in cs_cas/docs.py'
    assert grouped - used == set(), 'no endpoint uses these TAG_GROUPS tags'


def test_tags_are_named_after_the_spec_section():
    for _, _, operation in OPERATIONS:
        for tag in operation.get('tags', []):
            assert re.fullmatch(r'[A-Z]\d+\. [A-Z].*', tag), tag


@pytest.mark.parametrize('path', SCHEMA['paths'])
def test_paths_have_no_trailing_slash(path):
    assert not path.endswith('/')


def test_path_parameters_are_typed():
    untyped = []
    for path, method, operation in OPERATIONS:
        for parameter in operation.get('parameters', []):
            schema = parameter['schema']
            typed = schema.get('format') == 'uuid' or 'enum' in schema or '$ref' in schema or 'allOf' in schema
            if parameter['in'] == 'path' and not typed and parameter['name'] not in TEXT_PARAMETERS:
                untyped.append(f'{method.upper()} {path}: {parameter["name"]}')

    assert untyped == [], 'type path ids as uuid.UUID (or an enum)'


def test_operation_ids_are_unique():
    ids = [operation['operationId'] for _, _, operation in OPERATIONS]

    assert sorted({i for i in ids if ids.count(i) > 1}) == []


def test_no_path_is_shadowed_by_an_earlier_path_with_a_parameter():
    """
    Django tries paths in order, so /sailings/bulk must be declared before /sailings/{sailing_id}; otherwise "bulk" is
    read as a sailing id.
    """
    for pattern in api.urls[0]:
        route = 'api/' + str(pattern.pattern)
        url = '/' + re.sub(r'<[^>]+>', 'sample', route)

        assert resolve(url).route == route, f'{route} is shadowed by {resolve(url).route}'
