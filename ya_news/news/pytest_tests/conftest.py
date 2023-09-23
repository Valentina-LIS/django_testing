import datetime

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

PK = 1
HOME_URL = reverse('news:home')
DETAIL_URL = reverse('news:detail', args=(PK,))
LOGIN_URL = reverse('users:login')
EDIT_URL = reverse('news:edit', args=(PK,))
DELETE_URL = reverse('news:delete', args=(PK,))


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def news_pk_for_args(news):
    return news.pk,


@pytest.fixture
def comment_pk_for_args(comment):
    return comment.pk,


@pytest.fixture
def news_list():
    today = datetime.datetime.today()
    all_news = [News(title=f'Новость {index}',
                     text=f'Просто текст {index}',
                     date=today - datetime.timedelta(index))
                for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)]
    news = News.objects.bulk_create(all_news)
    return news


@pytest.fixture
def form_data(news):
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def comments(news, author):
    today = datetime.datetime.today()
    for index in range(2):
        comments_list = Comment.objects.create(
            news=news,
            text=f'Tекст {index}',
            author=author,
        )
        comments_list.created = today + timezone.timedelta(days=index)
        comments_list.save()
    return comments
