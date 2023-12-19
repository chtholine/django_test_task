import json
from random import randint, shuffle

import requests


def get_access_token(username, password):
    token_url = f'{base_url}token/'
    data = {'username': username, 'password': password}
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get('access')


def refresh_access_token(refresh_token):
    refresh_url = f'{base_url}token/refresh/'
    data = {'refresh': refresh_token}
    response = requests.post(refresh_url, data=data)
    if response.status_code == 200:
        return response.json().get('access')


def bot():
    # Sign up users
    for _ in range(config['number_of_users']):
        username = f'user{randint(1, 9999)}'
        password = 'password'
        user_data = {
            "username": username,
            "email": f"{username}@email.com",
            "password": password,
        }
        response = requests.post(f'{base_url}signup/', data=user_data)
        if response.status_code == 201:
            print(f"User '{username}' created successfully.")
        else:
            print(f"Failed to create User '{username}'.")

        auth_data = {
            "username": username,
            "password": password,
        }

        access_token = get_access_token(username, password)
        headers = {'Authorization': f'Bearer {access_token}'}

        # login
        auth_response = requests.post(f'{base_url}login/', headers=headers, data=auth_data)
        if auth_response.status_code == 200:
            # create and like posts functions
            create_posts(username, headers)
            like_posts(username, headers)
        else:
            print(f"Failed to authenticate User {username}.")


def create_posts(username, headers):
    for _ in range(randint(1, config['max_posts_per_user'])):
        post_name = f"Post #{randint(1, 9999)}"
        post_data = {
            "title": f"{post_name} by {username}",
            "content": "Post content",
        }
        response = requests.post(f'{base_url}posts/', headers=headers, json=post_data)
        if response.status_code == 201:
            print(f"{post_name} by {username} created successfully.")
        else:
            print(f"Failed creating {post_name}")


def get_all_posts(headers):
    all_posts = []

    next_url = f'{base_url}posts/'
    while next_url:
        response = requests.get(next_url, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                posts = data.get('results', [])
                all_posts.extend(posts)
                next_url = data.get('next')
            except Exception as e:
                print(f"Error processing posts response: {e}")
                print(response.content)
                break
        else:
            print(f"Failed to retrieve posts. Status code: {response.status_code}")
            break

    return all_posts


def like_posts(username, headers):
    all_posts = get_all_posts(headers)
    shuffle(all_posts)

    likes_to_give = min(config['max_likes_per_user'], len(all_posts))
    for j in range(likes_to_give):
        post = all_posts[j]
        post_id = post['id']
        like_data = {"post_id": post_id}
        response = requests.post(f'{base_url}posts/{post_id}/like/', headers=headers, json=like_data)
        if response.status_code == 200:
            print(f"{username} liked Post{post_id} with title: {post['title']}")
        else:
            print(f"Failed to like Post{post_id}. Status code: {response.status_code}")


if __name__ == "__main__":
    with open('bot_config.json') as f:
        config = json.load(f)
    base_url = config.get("base_url")
    bot()
