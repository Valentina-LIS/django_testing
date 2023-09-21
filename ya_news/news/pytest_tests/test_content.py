import pytest
from django.urls import reverse

from yanews import settings


@pytest.mark.django_db
def test_news_count(news_list, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert settings.NEWS_COUNT_ON_HOME_PAGE == news_count


@pytest.mark.django_db
def test_news_order(news_list, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_news = [news.date for news in object_list]
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
    url = reverse('news:detail', args=news_pk_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is expected_result


@pytest.mark.django_db
def test_sorted_comments(admin_client, comments, news_pk_for_args):
    url = reverse('news:detail', args=news_pk_for_args)
    response = admin_client.get(url)
    object_list = response.context['news'].comment_set.all()
    all_comments = [comment.created for comment in object_list]
    sorted_comments = sorted(all_comments)
    assert all_comments == sorted_comments
