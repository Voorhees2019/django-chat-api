from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import User
from dialogs.models import Thread, Message


class ThreadTestCase(APITestCase):
    def setUp(self) -> None:
        users = []
        for i in range(1, 4):
            user = self.create_user(
                username=f"test{i}",
                email=f"test{i}@gmail.com",
                first_name=f"first_name{i}",
                last_name=f"last_name{i}"
            )
            users.append(user)

        self.user1, self.user2, self.user3 = users
        self.thread = Thread.objects.create()
        self.thread.participants.set(users[:2])  # thread with `participants = [1, 2]`

        self.message = Message.objects.create(
            text="test message",
            thread=self.thread,
            sender=self.thread.participants.first(),
        )

        self.login_url = reverse("get_auth_token")
        self.thread_list_url = reverse("dialogs:thread_list")
        self.thread_detail_url = reverse(
            "dialogs:thread_detail", args=[1]
        )  # first thread
        self.message_list_url = reverse(
            "dialogs:message_list", args=[1]
        )  # messages from the first thread
        self.message_detail_url = reverse(
            "dialogs:message_detail", args=[1]
        )  # first message
        self.messages_read_until_url = reverse(
            "dialogs:messages_read_until", args=[1]
        )  # read messages until message_id from the first thread

    def create_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: str = "testpassword",
    ) -> User:
        user = User.objects.create(
            username=username, email=email, first_name=first_name, last_name=last_name
        )
        user.set_password(password)
        user.save()
        return user

    def _get_user_token(self, email="test@gmail.com", password="testpassword"):
        response = self.client.post(
            self.login_url, {"email": email, "password": password}
        )
        response_data = response.json()
        jwt_token = response_data.get("token", "")
        return f"JWT {jwt_token}"

    def test_thread_list(self):
        """
        Ensure user can get a thread list, only threads where user is in participants.
        """
        response = self.client.get(self.thread_list_url)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.get(
            self.thread_list_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data.get("count"), 1)
        self.assertIn(self.user1.id, data.get("results")[0]["participants"])

    def test_thread_create(self):
        """
        Ensure user can create a new thread object and the creator must be one of the participants.
        """
        data = {"participants": [1, 2]}
        response = self.client.post(self.thread_list_url, data=data)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.post(
            self.thread_list_url,
            data=data,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Thread between users 1 and 2 already exists
        # and we don't create a new one, but just return the existing one
        self.assertEqual(Thread.objects.count(), 1)

        response = self.client.post(
            self.thread_list_url,
            data={"participants": [1, 3]},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Creating a new thread between users 1 and 3
        self.assertEqual(Thread.objects.count(), 2)

        response = self.client.post(
            self.thread_list_url,
            data={"participants": [2, 3]},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        # Fail due to sending user in not in participants list
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            self.thread_list_url,
            data={"participants": []},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        # Fail due to no participants are provided
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            self.thread_list_url,
            data={"participants": [1, 2, 3]},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        # Fail due to greater than 2 participants are provided
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            self.thread_list_url,
            data={"participants": [1, 1]},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        # Fail due to provided participants are the same user
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_thread_detail(self):
        """
        Ensure user can get a certain thread object only if user is in thread participants.
        """
        response = self.client.get(self.thread_detail_url)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.get(
            self.thread_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Forcing authentication
        response = self.client.get(
            self.thread_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        # Fail due to user 3 is not a thread participant
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_thread_delete(self):
        """
        Ensure user can delete a certain thread object only if user is in thread participants.
        """
        response = self.client.delete(self.thread_detail_url)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.delete(
            self.thread_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        # Fail due to user 3 is not a thread participant
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Forcing authentication
        response = self.client.delete(
            self.thread_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_message_list(self):
        """
        Ensure user can get a message list for a certain thread
        only if user has permission to access this thread.
        """
        response = self.client.get(self.message_list_url)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.get(
            self.message_list_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Forcing authentication
        response = self.client.get(
            self.message_list_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        # Fail due to user 3 has no permission to access this thread
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_message_create(self):
        """
        Ensure user can create a new message object in existing thread
        only in user has permission to access this thread.
        """
        data = {"text": "hello there"}
        response = self.client.post(self.message_list_url, data)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.post(
            self.message_list_url,
            data=data,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user2.email),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 2)

        response = self.client.get(
            self.message_list_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user2.email),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]
        # ensure we have read all previous interlocutor's messages
        for message in data:
            if message.get("sender") != self.user2.id:
                self.assertEqual(message.get("is_read"), True)

        # Forcing authentication
        response = self.client.post(
            self.message_list_url,
            data={"text": "hi"},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Message.objects.count(), 2)

    def test_message_detail(self):
        """
        Ensure user can get a certain message object only if user is its sender.
        """
        response = self.client.get(self.message_detail_url)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.get(
            self.message_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.message_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        # Fail due to user 3 is not a message sender
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_message_partial_update(self):
        """
        Ensure user can update a certain message object only if user is its sender.
        """
        response = self.client.patch(self.message_detail_url)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.patch(
            self.message_detail_url,
            data={"text": "updated message 1"},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            self.message_detail_url,
            data={"text": "second update of message 1"},
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        # Fail due to user 3 is not a message sender
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_message_delete(self):
        """
        Ensure user can delete a certain message object only if user is its sender.
        """
        response = self.client.delete(self.message_detail_url)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.delete(
            self.message_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        # Fail due to user 3 is not a message sender
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Forcing authentication
        response = self.client.delete(
            self.message_detail_url,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user1.email),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_message_read_until(self):
        """
        Ensure user can mark interlocutor's messages as read
        in certain thread only if user is in thread participants.
        """
        data = {"message_id": 5}
        response = self.client.post(self.messages_read_until_url, data=data)
        # Fail due to Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Forcing authentication
        response = self.client.post(
            self.messages_read_until_url,
            data=data,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user3.email),
        )
        # Fail due to user 3 has no permission to access thread 1
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ensure the interlocutor's messages are still unread
        unread_messages = (
            Message.objects.unread()
            .filter(thread__pk=1, pk__lte=data["message_id"])
            .exclude(sender=self.user2)
        )
        for message in unread_messages:
            self.assertEqual(message.is_read, False)

        # read messages in thread until the given message_id
        response = self.client.post(
            self.messages_read_until_url,
            data=data,
            HTTP_AUTHORIZATION=self._get_user_token(email=self.user2.email),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ensure we have read all interlocutor's messages
        # which ids are lower or equal to provided message_id
        read_messages = (
            Message.objects.read()
            .filter(thread__pk=1, pk__lte=data["message_id"])
            .exclude(sender=self.user2)
        )
        for message in read_messages:
            self.assertEqual(message.is_read, True)
