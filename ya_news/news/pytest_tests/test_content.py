import pytest
from django.conf import settings

from news.forms import CommentForm
from news.pytest_tests.conftest import DETAIL_URL, HOME_URL


@pytest.mark.django_db
def test_news_count(news_list, client):
    response = client.get(HOME_URL)
    object_news = response.context['object_list']
    news_count = len(object_news)
    assert settings.NEWS_COUNT_ON_HOME_PAGE == news_count


@pytest.mark.django_db
def test_news_order(news_list, client):
    response = client.get(HOME_URL)
    object_news = response.context['object_list']
    all_news = [news.date for news in object_news]
    sorted_date = sorted(all_news, reverse=True)
    assert all_news == sorted_date


@pytest.mark.django_db
def test_form_in_any_users(client, admin_client, news):
    response = client.get(DETAIL_URL)
    admin_response = admin_client.get(DETAIL_URL)
    assert (isinstance(admin_response.context['form'], CommentForm)
            and 'form' not in response.context)


@pytest.mark.django_db
def test_sorted_comments(admin_client, comments):
    response = admin_client.get(DETAIL_URL)
    object_news = response.context['news'].comment_set.all()
    all_comments = [comment.created for comment in object_news]
    sorted_comments = sorted(all_comments)
    assert all_comments == sorted_comments
