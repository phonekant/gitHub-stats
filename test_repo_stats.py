from unittest.mock import patch
import repo_stats


def test_get_stats():
    # // fake three sequential API calls in the order get_stats makes them, no real network hit
    responses = [
        ({"stargazers_count": 10, "forks_count": 2, "language": "Python", "created_at": "2020-01-01"}, None),
        ({}, '<url?page=3>; rel="last"'),
        ({"total_count": 5}, None),
        ({"total_count": 1}, None),
    ]
    with patch("repo_stats._get", side_effect=responses):
        stats = repo_stats.get_stats("foo/bar")

    assert stats["stars"] == 10
    assert stats["contributors"] == 3
    assert stats["open_issues"] == 5
    assert stats["open_prs"] == 1


def test_last_page_count_no_header():
    assert repo_stats._last_page_count(None) == 1


if __name__ == "__main__":
    test_get_stats()
    test_last_page_count_no_header()
    print("ok")
