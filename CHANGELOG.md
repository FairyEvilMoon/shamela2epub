# Changelog

## 0.2.0

- Rebuilt the project around a Python-first architecture.
- Java helper now writes UTF-8 JSON to a temporary file instead of stdout to avoid Windows Arabic encoding loss.
- Avoids reading `store/book`, preventing mixed Lucene codec errors.
- Uses `master.db` for metadata and `book/<id>.db` for page/title mapping.
- Preserves scholarly page separators.

## 0.1.0

- Initial experimental prototype.
