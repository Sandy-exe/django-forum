import datetime, json
from contextlib import contextmanager
from django.test import TestCase, Client
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.urls import reverse

from django.contrib.auth.models import User
from .models import Channel, Thread, Comment

#Allow easy testing for validation errors
class ValidationErrorTestMixin(object):
    @contextmanager
    def assertValidationErrors(self, fields):
        try:
            yield
            raise AssertionError("ValidationError not raised")

        except ValidationError as e:
            self.assertEqual(set(fields), set(e.message_dict.keys()))

## Helper functions
def create_channel(name, owner, days=0):
    time = timezone.now() + datetime.timedelta(days=days)
    return Channel.objects.create(channel_name=name, owner=owner, pub_date=time)

def create_thread(channel, owner, name="name", desc="desc", days=0):
    time = timezone.now() + datetime.timedelta(days=days)
    return Thread.objects.create(channel=channel, owner=owner, thread_name=name, description=desc, pub_date=time)

def create_comment(thread, owner, text="text", days=0):
    time = timezone.now() + datetime.timedelta(days=days)
    return Comment.objects.create(thread=thread, text=text, owner=owner, pub_date=time)

##TODO: create_reply

## Channel tests
class ChannelTests(TestCase):
    channel_name = "Test-channel-123456789"
    owner_name = 'owner'

    def testNoChannel(self):
        response = self.client.get(reverse('forumapp:channel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No channels are available.")
        self.assertQuerysetEqual(response.context['channel_list'], [])

    def testChannelCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)

        c = create_channel(self.channel_name, owner)

        self.assertIn(c.channel_name, self.channel_name)
        self.assertEqual(len(c.channel_name), len(self.channel_name))

        response = self.client.get(reverse('forumapp:channel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.channel_name)

        c.delete()

        self.testNoChannel()

    def testChannelsAreDisplayed(self):
        owner = User.objects.create(username=self.owner_name)

        channel_name_2 = "testchannel2"
        c = create_channel(self.channel_name, owner)
        c = create_channel(channel_name_2, owner)

        response = self.client.get(reverse('forumapp:channel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.channel_name)
        self.assertContains(response, channel_name_2)

## Thread tests
class ThreadTests(TestCase):
    channel_name = "channelforthreadtest"
    owner_name = 'owner'
    thread_name = "threadtest"
    thread_desc = "descriptionforthreadtest"

    def testNoThread(self):
        owner = User.objects.create(username=self.owner_name)
        c = create_channel(self.channel_name, owner)

        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No threads are available.")
        self.assertQuerysetEqual(response.context['thread_list'], [])

    def testThreadCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)
        c = create_channel(self.channel_name, owner)
        t = create_thread(c, owner, self.thread_name, self.thread_desc)

        self.assertIn(t.thread_name, self.thread_name)
        self.assertEqual(len(t.thread_name), len(self.thread_name))

        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread_name)

        c.delete()

        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No threads are available.")
        self.assertQuerysetEqual(response.context['thread_list'], [])

    def testThreadsAreDisplayed(self):
        owner = User.objects.create(username=self.owner_name+'2')
        c = create_channel(self.channel_name, owner, -1)
        t1 = create_thread(c, owner, self.thread_name, self.thread_desc)
        t2 = create_thread(c, owner, self.thread_name[::-1], self.thread_desc)

        self.assertEquals(0, t1.thread_id)
        self.assertEquals(1, t2.thread_id)

        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread_name)
        self.assertContains(response, self.thread_name[::-1])

## Comment tests
class CommentTests(TestCase):
    owner_name = "testuser3"
    owner_name2 = "testuser4"
    owner_name3 = "testuser5"
    channel_name = "aaatestchannel"
    text = "test text :)"

    def testNoComment(self):
        owner = User.objects.create(username=self.owner_name)

        channel = create_channel(self.channel_name, owner)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2)

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': channel.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments are available.")
        self.assertQuerysetEqual(response.context['comment_list'], [])

    def testCommentCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)

        channel = create_channel(self.channel_name, owner)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2)
        owner3 = User.objects.create(username=self.owner_name3)

        c = create_comment(thread, owner3, self.text)

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': self.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.text)
        self.assertContains(response, self.owner_name3)

        c.delete()

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': self.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments are available.")
        self.assertQuerysetEqual(response.context['comment_list'], [])

    def testCommentsAreDisplayed(self):
        owner = User.objects.create(username=self.owner_name)
        channel = create_channel(self.channel_name, owner)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2)
        owner3 = User.objects.create(username=self.owner_name3)


        c1 = create_comment(thread, owner3, self.text)
        c2 = create_comment(thread, owner2, self.text[::-1])

        self.assertEquals(0, c1.comment_id)
        self.assertEquals(1, c2.comment_id)

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': self.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.text)
        self.assertContains(response, self.text[::-1])

    # TODO: add test for is_recent
    def testCommentIsRecent(self):
        owner = User.objects.create(username=self.owner_name)
        channel = create_channel(self.channel_name, owner)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2)
        owner3 = User.objects.create(username=self.owner_name3)

        c1 = create_comment(thread, owner3, days=-2)
        c2 = create_comment(thread, owner3, days=-0.5)
        c3 = create_comment(thread, owner2, days=0)
        c4 = create_comment(thread, owner, days=1)

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': self.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertIs(c1.is_recent(), False)
        self.assertIs(c2.is_recent(), True)
        self.assertIs(c3.is_recent(), True)
        self.assertIs(c4.is_recent(), False)

## Preserve data when a User is deleted
## Cascade-delete when channels/threads are removed (preserving users)
class CascadeDeleteTests(TestCase):
    username = "randomuser91387245"
    channel_name = "channel1981719"
    channel_name2 = "asfsga"
    channel_name3 = "nhjtgrew"
    thread_name = "aaa"
    thread_name2 = "bbb"
    thread_name3 = "ccc"
    def testUserDelete(self):
        owner = User.objects.create(username=self.username)
        otheruser = User.objects.create(username=self.username[::-1])

        # Create a channel
        channel = create_channel(self.channel_name, owner)
        subthread = create_thread(channel, owner, self.thread_name)
        thread_id1 = subthread.thread_id

        subcomment = create_comment(subthread, owner)
        comment_id1 = subcomment.comment_id

        # Create a thread under another users channel
        otherchannel = create_channel(self.channel_name2, otheruser)
        thread = create_thread(otherchannel, owner, self.thread_name2)


        # Create a comment under another users channel and thread
        otherthread = create_thread(otherchannel, otheruser, self.thread_name3)
        thread_id2 = otherthread.thread_id

        otherthread_id = otherthread.thread_id
        comment = create_comment(otherthread, owner)
        comment_id2 = comment.comment_id

        owner.delete()

        # Channel and its children should be gone (this tests cascade deletion
        #   for channels->threads->comments)
        self.assertEqual(False, Channel.objects.filter(owner=None).exists())
        self.assertEqual(False, Thread.objects.filter(channel=None).exists())
        self.assertEqual(False, Comment.objects.filter(thread=None).exists())

        # Verify that the thread and comment under the other user's channel should still exist
        self.assertEqual(True, Channel.objects.filter(channel_name=self.channel_name2).exists())
        self.assertEqual(True, Thread.objects.filter(channel__channel_name=self.channel_name2, thread_id=thread_id2).exists())
        self.assertEqual(True, Comment.objects.filter(thread__channel__channel_name=self.channel_name2, thread__thread_id=otherthread_id, comment_id=comment_id2).exists())

    ## Tests whether a channel is correctly passed off to one of the channel moderators
    ## if a channel moderator is specified when the owner is deleted
    def testChannelOwnerPassOff(self):
        owner = User.objects.create(username=self.username)
        otheruser = User.objects.create(username=self.username[::-1])

        channel = create_channel(self.channel_name, owner)
        subthread = create_thread(channel, owner, self.thread_name)

        # set moderator
        channel.moderators = json.dumps([otheruser.username])
        channel.save()

        #delete channel and see if the owner was changed to to the otheruser
        owner.delete()

        self.assertEqual(True, Channel.objects.filter(channel_name=self.channel_name).exists())
        self.assertEqual(self.username[::-1], Channel.objects.get(channel_name=self.channel_name).owner.username)

    ## Test whether deleting a thread preserves its channel and deletes its comments
    def testThreadDelete(self):
        owner = User.objects.create(username=self.username)
        
        # Create a channel
        channel = create_channel(self.channel_name, owner)
        thread = create_thread(channel, owner, self.thread_name)
        thread_id = thread.thread_id

        comment = create_comment(thread, owner)
        comment_id = comment.comment_id

        thread.delete()

        self.assertEquals(True, User.objects.filter(username=self.username).exists())
        self.assertEquals(True, Channel.objects.filter(channel_name=self.channel_name).exists())
        self.assertEquals(False, Thread.objects.filter(channel__channel_name=self.channel_name, thread_id=thread_id).exists())
        self.assertEquals(False, Thread.objects.filter(channel=None).exists())
        self.assertEquals(False, Comment.objects.filter(thread__thread_id=thread_id, comment_id=comment_id).exists())
        self.assertEquals(False, Comment.objects.filter(thread=None).exists())
    
    ## Test whether deleting a comment preserves its thread
    def testCommentDelete(self):
        owner = User.objects.create(username=self.username)
        
        # Create a channel
        channel = create_channel(self.channel_name, owner)
        thread = create_thread(channel, owner, self.thread_name)
        thread_id = thread.thread_id

        comment = create_comment(thread, owner)
        comment_id = comment.comment_id

        comment.delete()

        self.assertEquals(True, User.objects.filter(username=self.username).exists())
        self.assertEquals(True, Channel.objects.filter(channel_name=self.channel_name).exists())
        self.assertEquals(True, Thread.objects.filter(channel__channel_name=self.channel_name, thread_id=thread_id).exists())
        self.assertEquals(False, Comment.objects.filter(thread__thread_id=thread_id, comment_id=comment_id).exists())
        self.assertEquals(False, Comment.objects.filter(thread=None).exists())

#Confirm primary keys work as expected (esp. since comment has 3 primary keys and thread has 2)
class UniqueValidationTests(ValidationErrorTestMixin, TestCase):
    username1 = "asdjghuetjw"
    username2 = username1[:8]
    channel_name1 = "channel1981719"
    channel_name2 = channel_name1[:10]

    def testUniqueUser(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)

        with self.assertValidationErrors(['username']):
            User(username=self.username1).validate_unique()


    def testUniqueChannel(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)
        c1 = create_channel(self.channel_name1, user1)
        c2 = create_channel(self.channel_name2, user2)
        c3 = Channel(channel_name=self.channel_name1, owner=user1, pub_date=timezone.now())
        c4 = Channel(channel_name=self.channel_name2, owner=user1, pub_date=timezone.now())

        with self.assertValidationErrors(['channel_name']):
            c3.validate_unique()

        with self.assertValidationErrors(['channel_name']):
            c4.validate_unique()

    def testUniqueThread(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)
        c1 = create_channel(self.channel_name1, user1)
        c2 = create_channel(self.channel_name2, user2)
        t1 = create_thread(c1, user1)
        t2 = create_thread(c1, user1)
        t3 = create_thread(c2, user2)
        t4 = create_thread(c2, user1)

        self.assertEquals(t1.thread_id, t3.thread_id)
        self.assertEquals(t2.thread_id, t4.thread_id)

        t5 = Thread(thread_id=0, channel=c1, owner=user2, thread_name="aa", description="bb", pub_date=timezone.now())

        with self.assertValidationErrors(['channel', 'thread_id']):
            t5.validate_unique()

    def testUniqueComment(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)
        c1 = create_channel(self.channel_name1, user1)
        c2 = create_channel(self.channel_name2, user2)
        t1 = create_thread(c1, user1)
        t2 = create_thread(c2, user2)
        co1 = create_comment(t1, user1)
        co2 = create_comment(t1, user2)
        co3 = create_comment(t2, user2)
        co4 = create_comment(t2, user2)

        self.assertEquals(co1.comment_id, co3.comment_id)
        self.assertEquals(co2.comment_id, co4.comment_id)

        co5 = Comment(comment_id=0, thread=t1, owner=user2, text="", pub_date=timezone.now())
        co6 = Comment(comment_id=1, thread=t1, owner=user2, text="", pub_date=timezone.now())
        co7 = Comment(comment_id=1, thread=t2, owner=user1, text="", pub_date=timezone.now())

        with self.assertValidationErrors(['thread', 'comment_id']):
            co5.validate_unique()

        with self.assertValidationErrors(['thread', 'comment_id']):
            co6.validate_unique()

        with self.assertValidationErrors(['thread', 'comment_id']):
            co7.validate_unique()
