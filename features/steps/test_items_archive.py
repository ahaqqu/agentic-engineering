from pytest_bdd import scenario


@scenario("../items_archive.feature", "Archive endpoint returns the updated row fragment")
def test_archive_api():
    pass


@scenario("../items_archive.feature", "A non-member cannot archive the item")
def test_archive_non_member():
    pass


@scenario("../items_archive.feature", "Unauthenticated archive attempt is rejected")
def test_archive_unauth():
    pass


@scenario("../items_archive.feature", "Toggling archive updates the row without a page reload")
def test_archive_ui():
    pass


@scenario("../items_archive.feature", "Archived state survives a refresh")
def test_archive_persists():
    pass
