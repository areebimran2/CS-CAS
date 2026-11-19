from django.db import transaction
from django.db.models import Count

from catalogs.models import CabinCategory
from common.exceptions import ShipArchivedError, ValidationFailedError
from common.services import delete_if_unused, update_instance
from ships_cabins.models import Cabin, Ship


def cabins_matching(ship: Ship, *, category_ids=None, decks=None, cabin_ids=None):
    """
    The ship's current cabins, narrowed by any of the given category ids, decks or cabin ids. Bulk pricing uses this
    to target "all Premium cabins" or "all Main deck cabins" (spec G2).
    """
    cabins = ship.cabin_set.filter(is_archived=False)
    if category_ids is not None:
        cabins = cabins.filter(category_id__in=category_ids)
    if decks is not None:
        cabins = cabins.filter(deck__in=decks)
    if cabin_ids is not None:
        cabins = cabins.filter(id__in=cabin_ids)
    return cabins


def decks(ship: Ship):
    """Each deck that has current cabins, with how many."""
    return (ship.cabin_set.filter(is_archived=False).exclude(deck=None)
            .values('deck').annotate(cabin_count=Count('id')).order_by('deck'))


@transaction.atomic
def create_cabin(ship: Ship, **fields) -> Cabin:
    """Create one cabin. A number already used on the ship is reported as 409 DUPLICATE by the database."""
    _require_current(ship)
    _require_active_category(fields['category_id'])
    return Cabin.objects.create(ship=ship, **_with_default_name(fields))


@transaction.atomic
def create_cabins(ship: Ship, rows: list[dict]) -> list[Cabin]:
    """
    Create many cabins at once, or none: every problem in every row is reported together, with the row's position,
    before anything is saved.
    """
    _require_current(ship)
    errors = _bulk_errors(ship, rows)
    if errors:
        raise ValidationFailedError(detail='No cabins were created.', errors=errors)
    created = Cabin.objects.bulk_create([Cabin(ship=ship, **_with_default_name(row)) for row in rows])
    return list(Cabin.objects.filter(id__in=[cabin.id for cabin in created]).select_related('category'))


@transaction.atomic
def update_cabin(cabin: Cabin, changes: dict) -> Cabin:
    """Apply a partial update. A cleared name falls back to "Cabin <number>"."""
    changes = dict(changes)
    if 'category_id' in changes and changes['category_id'] != cabin.category_id:
        _require_active_category(changes['category_id'])
    if 'name' in changes and not changes['name']:
        changes['name'] = _default_name(changes.get('number', cabin.number))
    return update_instance(cabin, changes)


@transaction.atomic
def set_cabin_archived(cabin: Cabin, archived: bool) -> Cabin:
    return update_instance(cabin, {'is_archived': archived})


@transaction.atomic
def delete_cabin(cabin: Cabin) -> None:
    """Delete a cabin that nothing refers to (cabin maps, pricing, discounts, holds or bookings)."""
    delete_if_unused(cabin)


# -- Rules

NO_ACTIVE_CATEGORY = 'No active cabin category with this id'


def _default_name(number):
    return f'Cabin {number}'


def _with_default_name(fields):
    return {**fields, 'name': fields.get('name') or _default_name(fields['number'])}


def _require_current(ship):
    if ship.is_archived:
        raise ShipArchivedError(detail='Cabins can\'t be added to an archived ship. Unarchive it first.')


def _require_active_category(category_id):
    if not CabinCategory.objects.filter(id=category_id, is_active=True).exists():
        raise ValidationFailedError(errors=[{'field': 'category_id', 'message': NO_ACTIVE_CATEGORY}])


def _bulk_errors(ship, rows):
    """Every problem in the rows, as errors naming the row: duplicate numbers and unusable categories."""
    category_ids = {row['category_id'] for row in rows}
    active_categories = set(CabinCategory.objects.filter(id__in=category_ids, is_active=True)
                            .values_list('id', flat=True))
    # The number column ignores case, so this lookup finds "12a" when the request says "12A".
    taken = {number.casefold() for number in
             ship.cabin_set.filter(number__in=[row['number'] for row in rows]).values_list('number', flat=True)}

    errors, seen = [], set()
    for index, row in enumerate(rows):
        number = row['number'].casefold()
        if number in taken:
            errors.append({'field': f'cabins[{index}].number', 'message': 'Already used on this ship'})
        elif number in seen:
            errors.append({'field': f'cabins[{index}].number', 'message': 'Appears more than once in this request'})
        seen.add(number)
        if row['category_id'] not in active_categories:
            errors.append({'field': f'cabins[{index}].category_id', 'message': NO_ACTIVE_CATEGORY})
    return errors
