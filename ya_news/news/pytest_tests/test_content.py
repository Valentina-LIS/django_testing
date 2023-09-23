import pytest

from django.conf import settings

from news.pytest_tests.conftest import HOME_URL, DETAIL_URL


@pytest.mark.django_db
def test_news_count(news_list, client):
    url = HOME_URL
    response = client.get(url)
    object_news = response.context['object_list']
    news_count = len(object_news)
    assert settings.NEWS_COUNT_ON_HOME_PAGE == news_count


@pytest.mark.django_db
def test_news_order(news_list, client):
    url = HOME_URL
    response = client.get(url)
    object_news = response.context['object_list']
    all_news = [news.date for news in object_news]
    sorted_date = sorted(all_news, reverse=True)
    assert all_news == sorted_date


@pytest.mark.parametrize(
    'parametrized_client, expected_result',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
@pytest.mark.django_db
def test_form_in_any_users(parametrized_client,
                           expected_result,
                           news_pk_for_args):
    url = DETAIL_URL
    response = parametrized_client.get(url)
    assert ('form' in response.context) is expected_result


@pytest.mark.django_db
def test_sorted_comments(admin_client, comments):
    url = DETAIL_URL
    response = admin_client.get(url)
    object_news = response.context['news'].comment_set.all()
    all_comments = [comment.created for comment in object_news]
    sorted_comments = sorted(all_comments)
    assert all_comments == sorted_comments
