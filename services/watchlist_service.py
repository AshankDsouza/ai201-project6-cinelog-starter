"""
services/watchlist_service.py — CineLog

Business logic for managing a user's watchlist (films they want to see).
All functions follow the project's verb_to_noun naming convention.
"""

from app import db
from models import Film, WatchlistEntry


class FilmNotFoundError(Exception):
    """Raised when a film_id does not exist in the database."""
    pass


class AlreadyOnWatchlistError(Exception):
    """Raised when a film is already on the user's watchlist."""
    pass


class NotOnWatchlistError(Exception):
    """Raised when trying to remove a film that isn't on the watchlist."""
    pass


def add_to_watchlist(user_id, film_id, public=True):
    """
    Add a film to a user's watchlist (i.e., save it to watch later).

    Args:
        user_id (str): UUID of the user.
        film_id (int): ID of the film.
        public (bool): Whether the watchlist entry is publicly visible. Defaults to True.

    Returns:
        WatchlistEntry: The newly created entry.

    Raises:
        FilmNotFoundError: If film_id does not exist.
    """
    film = Film.query.get(film_id)
    if film is None:
        raise FilmNotFoundError(f"No film found with id '{film_id}'")

    existing = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    if existing:
        raise AlreadyOnWatchlistError(
            f"Film '{film_id}' is already on this user's watchlist"
        )

    entry = WatchlistEntry(user_id=user_id, film_id=film_id, public=public)
    db.session.add(entry)
    db.session.commit()
    return entry


def remove_from_watchlist(user_id, film_id):
    """
    Remove a film from a user's watchlist.

    Args:
        user_id (str): UUID of the user.
        film_id (int): ID of the film.

    Returns:
        bool: True if the entry was removed.

    Raises:
        NotOnWatchlistError: If the film is not on the user's watchlist.
    """
    entry = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    if entry is None:
        raise NotOnWatchlistError(
            f"Film '{film_id}' is not on this user's watchlist"
        )

    db.session.delete(entry)
    db.session.commit()
    return True


def get_watchlist(user_id):
    """
    Return all films on a user's watchlist, sorted by date added (newest first).

    Args:
        user_id (str): UUID of the user.

    Returns:
        list[dict]: List of film dicts with date_added and public from the entry attached.
    """
    entries = (
        WatchlistEntry.query
        .filter_by(user_id=user_id)
        .order_by(WatchlistEntry.date_added.desc())
        .all()
    )

    result = []
    for entry in entries:
        film_dict = entry.film.to_dict()
        film_dict["date_added"] = entry.date_added.isoformat()
        film_dict["public"] = entry.public
        result.append(film_dict)

    return result
