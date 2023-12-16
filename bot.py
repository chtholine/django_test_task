import json
import random
import requests

BASE_URL = 'http://127.0.0.1:8000/api/v1/'  # Replace with your Django app's API base URL


def read_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config


def signup_users(number_of_users):
    users = []
    for _ in range(number_of_users):
        username = f'user_{random.randint(1, 1000)}'
        email = f'{username}@example.com'
        password = 'password123'  # You may want to generate a random password

        # Signup
        signup_response = requests.post(
            f'{BASE_URL}signup/',
            data={'username': username, 'email': email, 'password': password}
        )

        if signup_response.status_code == 201:
            # Login to obtain JWT token
            login_response = requests.post(
                f'{BASE_URL}login/',
                data={'username': username, 'password': password}
            )

            if login_response.status_code == 200:
                # Retrieve user details after login
                user_id = get_user_id(login_response.json()['access'])
                if user_id is not None:
                    user_data = {
                        'id': user_id,
                        'username': username,
                        'token': login_response.json()['access'],
                    }
                    users.append(user_data)
                else:
                    print(f'Error retrieving user details after login.')
            else:
                print(f'Error logging in after signup: {login_response.text}')
        else:
            print(f'Error creating user: {signup_response.text}')

    return users


def get_user_id(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}users/', headers=headers)

    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f'Error retrieving user ID: {response.text}')
        return None


def create_posts(users, max_posts_per_user):
    for user in users:
        user_id = user['id']
        token = user['token']
        headers = {'Authorization': f'Bearer {token}'}

        num_posts = random.randint(1, max_posts_per_user)
        for _ in range(num_posts):
            content = f'Post content by user {user_id}'
            requests.post(
                f'{BASE_URL}posts/',
                headers=headers,
                data={'user': user_id, 'content': content}
            )


def like_posts(users, max_likes_per_user):
    for user in users:
        user_id = user['id']
        token = user['token']
        headers = {'Authorization': f'Bearer {token}'}

        num_likes = random.randint(1, max_likes_per_user)
        posts = requests.get(f'{BASE_URL}posts/').json()

        for _ in range(num_likes):
            post_id = random.choice(posts)['id']
            requests.post(
                f'{BASE_URL}/api/posts/{post_id}/like/',
                headers=headers,
                data={'user': user_id, 'content': 'Like content'}  # Adjust payload as needed
            )


if __name__ == "__main__":
    config = read_config('bot_config.json')  # Replace with the path to your config file

    number_of_users = config['number_of_users']
    max_posts_per_user = config['max_posts_per_user']
    max_likes_per_user = config['max_likes_per_user']

    users = signup_users(number_of_users)

    if users:
        create_posts(users, max_posts_per_user)
        like_posts(users, max_likes_per_user)
    else:
        print('Signup failed for all users.')
