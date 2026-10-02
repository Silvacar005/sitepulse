from sitepulse.scanner import analyze_html, normalize_url


def test_normalize_url_adds_https():
    assert normalize_url("example.com") == "https://example.com"


def test_good_page_has_no_basic_content_issues():
    html = """
    <html>
      <head>
        <title>Example</title>
        <meta name="description" content="A useful description">
      </head>
      <body>
        <h1>Welcome</h1>
        <img src="logo.png" alt="Example logo">
        <a href="/about">About</a>
        <a href="https://openai.com">External</a>
      </body>
    </html>
    """

    result = analyze_html("https://example.com", html)

    assert result.title == "Example"
    assert result.h1_count == 1
    assert result.images_missing_alt == 0
    assert result.internal_links == ["https://example.com/about"]
    assert result.external_links == ["https://openai.com"]
    assert result.issues == []


def test_missing_content_creates_issues():
    html = """
    <html>
      <head></head>
      <body>
        <img src="photo.jpg">
      </body>
    </html>
    """

    result = analyze_html("https://example.com", html)
    messages = [issue.message for issue in result.issues]

    assert "Page is missing a title." in messages
    assert "Page is missing a meta description." in messages
    assert "Page does not contain an H1 heading." in messages
    assert "1 image(s) are missing useful alt text." in messages
