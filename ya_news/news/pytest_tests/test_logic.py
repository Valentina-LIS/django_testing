from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from news.pytest_tests.conftest import (LOGIN_URL, DETAIL_URL,
                                        EDIT_URL, DELETE_URL)


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data):
    comments_count = set(Comment.objects.all())
    url = DETAIL_URL
    response = client.post(url, data=form_data)
    login_url = LOGIN_URL
    expected_redirect = f'{login_url}?next={url}'
    assertRedirects(response, expected_redirect)
    all_comments = set(Comment.objects.all())
    assert comments_count == all_comments


@pytest.mark.django_db
def test_user_can_create_comment(author_client, form_data,
                                 author, news):
    url = DETAIL_URL
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, form_data):
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    url = DETAIL_URL
    response = admin_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_data,
                                 comment, author):
    url = EDIT_URL
    news_url = DETAIL_URL + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, news_url)
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == form_data['text']
    assert comment.text == comment_from_db.text
    assert comment.author == author
    assert comment.created == comment_from_db.created
    assert comment.news == comment_from_db.news


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = DELETE_URL
    news_url = DETAIL_URL + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, news_url)
    assert response != news_url
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  comment_pk_for_args):
    assert Comment.objects.count() == 1
    url = DELETE_URL
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client,
                                                comment,
                                                form_data):
    comment_object = comment.text
    url = EDIT_URL
    response = reader_client.post(url, data=form_data)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    expected_count = 1
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == expected_count
    assert comment.text == comment_object
