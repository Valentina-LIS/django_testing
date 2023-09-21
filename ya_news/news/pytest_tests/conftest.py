import datetime

import pytest
from django.utils import timezone

from news.models import News, Comment
from yanews import settings


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


today = datetime.datetime.today()


@pytest.fixture
def news_list():
    all_news = [News(title=f'Новость {index}',
                     text=f'Просто текст {index}',
                     date=today - datetime.timedelta(index))
                for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)]
    news = News.objects.bulk_create(all_news)
    return news


@pytest.fixture
def form_data(news):
    return {
        'news': news,
        'text': 'Новый текст',
        'created': timezone.now()
    }


@pytest.fixture
def comments(news, author):
    comments_list = [Comment(
        news=news,
        text='Текст',
        created=today + timezone.timedelta(days=index),
        author=author
    )
        for index in range(2)]
    all_comments = Comment.objects.bulk_create(comments_list)
    return all_comments
