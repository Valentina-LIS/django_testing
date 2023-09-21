from http import HTTPStatus

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            form_data,
                                            news_pk_for_args):
    url = reverse('news:detail', args=news_pk_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_redirect = f'{login_url}?next={url}'
    assertRedirects(response, expected_redirect)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(admin_client, form_data, news_pk_for_args):
    url = reverse('news:detail', args=news_pk_for_args)
    admin_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == form_data['text']
    assert comment.news == form_data['news']


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, news_pk_for_args, form_data):
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    url = reverse('news:detail', args=news_pk_for_args)
    response = admin_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_cant_edit_comment_using_bad_words(author_client,
                                                  comment_pk_for_args,
                                                  form_data):
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    url = reverse('news:edit', args=comment_pk_for_args)
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comment = Comment.objects.get(pk=comment_pk_for_args[0])
    assert comment.text != form_data['text']


@pytest.mark.django_db
def test_author_can_edit_comment(author_client,
                                 news_pk_for_args,
                                 comment_pk_for_args,
                                 form_data):
    url = reverse('news:edit', args=comment_pk_for_args)
    news_url = reverse('news:detail', args=news_pk_for_args) + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, news_url)
    comment = Comment.objects.first()
    assert comment.text == form_data['text']
    assert comment.news == form_data['news']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, news_pk_for_args):
    url = reverse('news:delete', args=(comment.pk,))
    news_url = reverse('news:detail', args=news_pk_for_args) + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, news_url)
    with pytest.raises(ObjectDoesNotExist):
        Comment.objects.get(pk=comment.pk)


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  comment_pk_for_args):
    assert Comment.objects.count() == 1
    url = reverse('news:delete', args=comment_pk_for_args)
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client,
                                                comment,
                                                form_data):
    url = reverse('news:edit', args=(comment.pk,))
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
