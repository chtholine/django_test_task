import requests
from random import randint
import json


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
        username = f'sarrahh{randint(1, 1000)}'
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
            # create and like posts function
            create_posts(username, headers)
            get_and_like_posts(username, headers)
        else:
            print(f"Failed to authenticate User {username}.")


def create_posts(username, headers):
    for _ in range(randint(1, config['max_posts_per_user'])):
        post_name = f"Post #{randint(100, 999)}"
        post_data = {
            "title": f"{post_name} by {username}",
            "content": "Post content",
            # Add any other required fields here
        }
        response = requests.post(f'{base_url}posts/', headers=headers, json=post_data)
        if response.status_code == 201:
            print(f"{post_name} by {username} created successfully.")
        else:
            print(f"Failed creating {post_name}")


def get_and_like_posts(username, headers):
    response = requests.get(f'{base_url}posts/', headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            posts = data.get('results', [])
            post_ids = [post['id'] for post in posts]
            for j in range(randint(1, min(config['max_likes_per_user'], len(post_ids)))):
                post_id = post_ids[j]
                like_data = {"post_id": post_id}
                response = requests.post(f'http://127.0.0.1:8000/api/v1/posts/{post_id}/like/', headers=headers,
                                         json=like_data)
                if response.status_code == 200:
                    print(f"{username} liked Post{post_id} successfully.")
        except Exception as e:
            print(f"Error processing posts response: {e}")
            print(response.content)
    else:
        print(f"Failed to retrieve posts. Status code: {response.status_code}")


if __name__ == "__main__":
    base_url = "http://127.0.0.1:8000/api/v1/"
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
    bot()
