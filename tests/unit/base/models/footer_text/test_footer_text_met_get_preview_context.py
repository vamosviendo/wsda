def test_devuelve_context_con_footer_text(footer_text, site, client):
    request = client.get("/")
    assert \
        footer_text.get_preview_context(request, "") == \
        {"footer_text": footer_text.body}
