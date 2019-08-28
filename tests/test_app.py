from app import app


# @pytest.mark.options(debug=False)
def test_app():
    assert not app.debug, "Ensure the app not in debug mode"
