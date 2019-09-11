# Upgrading

```
pip install -U gns3fy
```

# Releases

## 0.3.0

**Enhacement:**

- `tox` for pipeline testing. https://github.com/davidban77/gns3fy/pull/15
- `projects_summary` and `templates_summary` methods for `Gns3Connector`. https://github.com/davidban77/gns3fy/pull/17
- Improved `nodes_inventory` method. https://github.com/davidban77/gns3fy/pull/23
- Refactor of `Node` creation, basically changed the API endpoint from Node to Template. https://github.com/davidban77/gns3fy/pull/27

## 0.2.0

**New features:**

- Ability to create `Project`, `Node` and `Link` instances
- Created most of the methods to interact with the REST API Endpoints.
- Added some commodity methods like `nodes_summary`
- Created the `docs`
- Improved the tests and coverage
- Added CircleCI with the following checks:
    - flake8
    - black formatting
    - pytest

## 0.1.1

**Enhancement:**
- Adding `Gns3Connector` method `get_version`

## 0.1.0

- Initial Push
