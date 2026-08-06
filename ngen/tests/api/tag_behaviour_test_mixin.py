from rest_framework import status


class TagBehaviourTestMixin:
    """
    Every serializer that mixes TagSerializerMixin in has to answer the same way,
    so the behaviour is written once and each resource says how to build one of
    its objects. Mix this into the api test case of the resource.
    """

    #: The tags every test starts from
    initial_tags = ["urgent", "phishing"]

    def create_tagged_object(self, tags):
        """
        Create an object of the resource with the given tags and return it
        """
        raise NotImplementedError

    def tagged_object_url(self, obj):
        """
        The detail url of an object of the resource
        """
        raise NotImplementedError

    def create_data(self):
        """
        Everything a POST of the resource needs, tags aside
        """
        raise NotImplementedError

    def full_update_data(self, obj):
        """
        Everything a PUT of the object needs, tags aside
        """
        raise NotImplementedError

    def partial_update_data(self, obj):
        """
        A single field of the object that has nothing to do with the tags
        """
        raise NotImplementedError

    def assertTags(self, obj, tags):
        obj.refresh_from_db()
        self.assertCountEqual(obj.tags.names(), tags)

    # Read

    def test_tags_are_read_on_the_detail(self):
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.get(self.tagged_object_url(obj))

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(response.data["tags"], self.initial_tags)

    # Create

    def test_tags_are_set_on_creation(self):
        response = self.client.post(
            self.url_list, data={**self.create_data(), "tags": self.initial_tags}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertCountEqual(response.data["tags"], self.initial_tags)

    def test_tags_are_empty_when_they_are_not_sent_on_creation(self):
        response = self.client.post(self.url_list, data=self.create_data())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["tags"], [])

    # Partial update

    def test_tags_survive_a_partial_update_that_does_not_send_them(self):
        """
        This is what closing a case from the list does: it sends the state and
        nothing else, and it used to leave the object with no tags
        """
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.patch(
            self.tagged_object_url(obj), data=self.partial_update_data(obj)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertCountEqual(response.data["tags"], self.initial_tags)
        self.assertTags(obj, self.initial_tags)

    def test_tags_are_replaced_by_a_partial_update_that_sends_them(self):
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.patch(
            self.tagged_object_url(obj), data={"tags": ["only-this-one"]}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, ["only-this-one"])

    def test_tags_are_emptied_by_a_partial_update_with_an_empty_list(self):
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.patch(
            self.tagged_object_url(obj), data={"tags": []}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, [])

    def test_tags_are_emptied_by_a_partial_update_with_null(self):
        """
        The field takes null, so it has to mean the same as an empty list
        """
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.patch(
            self.tagged_object_url(obj), data={"tags": None}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, [])

    # Full update

    def test_tags_survive_a_full_update_that_does_not_send_them(self):
        """
        A form field with no value is not sent at all, so an absent field cannot
        mean 'delete them': it is the same as a partial update
        """
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.put(
            self.tagged_object_url(obj), data=self.full_update_data(obj)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, self.initial_tags)

    def test_tags_are_replaced_by_a_full_update_that_sends_them(self):
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.put(
            self.tagged_object_url(obj),
            data={**self.full_update_data(obj), "tags": ["only-this-one"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, ["only-this-one"])

    def test_tags_are_emptied_by_a_full_update_with_an_explicit_empty_list(self):
        """
        The shape the case form sends to empty them, since form data cannot
        carry an empty list
        """
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.put(
            self.tagged_object_url(obj),
            data={**self.full_update_data(obj), "tags": "[]"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, [])

    # The shapes the forms send over form data

    def test_tags_can_be_sent_as_a_comma_separated_string(self):
        """
        The shape the event form sends, which appends the whole list at once
        """
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.patch(
            self.tagged_object_url(obj), data={"tags": "one,two"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, ["one", "two"])

    def test_tags_are_emptied_by_an_empty_string(self):
        """
        The shape the event form sends when the object was left with no tags
        """
        obj = self.create_tagged_object(self.initial_tags)

        response = self.client.patch(self.tagged_object_url(obj), data={"tags": ""})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTags(obj, [])
