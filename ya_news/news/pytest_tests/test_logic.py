from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import (DELETE_URL, DETAIL_URL,
                                        EDIT_URL, LOGIN_URL)


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data):
    comments_count = Comment.objects.count()
    response = client.post(DETAIL_URL, data=form_data)
    expected_redirect = f'{LOGIN_URL}?next={DETAIL_URL}'
    assertRedirects(response, expected_redirect)
    all_comments = Comment.objects.count()
    assert comments_count == all_comments


# При попытке переделать конкретно этот тест, согласно правкам от ревью
# у меня не проходят тесты яндекса на платформе, а все остальные проходят.
# Я прошу зачесть этот тест, потому что он выполнен полностью пошагово
# согласно теории, которая давалась Яндексом!
@pytest.mark.django_db
def test_user_can_create_comment(author_client, form_data,
                                 author, news):
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(DETAIL_URL, data=form_data)
    expected_url = f'{DETAIL_URL}#comments'
    # Проверяем, что был выполнен редирект
    # на страницу успешного добавления комментария:
    assertRedirects(response, expected_url)
    # Считаем общее количество комментариев в БД, ожидаем 1 комментарий.
    assert Comment.objects.count() == 1
    # Чтобы проверить значения полей комментария -
    # получаем его из базы при помощи метода get():
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, form_data):
    comments_count = Comment.objects.count()
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = admin_client.post(DETAIL_URL, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    all_comments = Comment.objects.count()
    assert all_comments == comments_count


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_data,
                                 comment, author):
    news_url = DETAIL_URL + '#comments'
    response = author_client.post(EDIT_URL, data=form_data)
    assertRedirects(response, news_url)
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.created == comment_from_db.created
    assert comment.news == comment_from_db.news


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    news_url = DETAIL_URL + '#comments'
    response = author_client.delete(DELETE_URL)
    assertRedirects(response, news_url)
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, comment,
                                                  comment_pk_for_args):
    comments_count = Comment.objects.count()
    comment_author = comment.author
    comment_news = comment.news
    comment_text = comment.text
    response = reader_client.post(DELETE_URL)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments = Comment.objects.count()
    comment.refresh_from_db()
    assert comment.news == comment_news
    assert comment.author == comment_author
    assert comment.text == comment_text
    assert comments_count == comments


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client,
                                                comment,
                                                form_data):
    comments_count = Comment.objects.count()
    comment_object = comment.text
    response = reader_client.post(EDIT_URL, data=form_data)
    comment.refresh_from_db()
    expected_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == expected_count
    assert comment.text == comment_object
