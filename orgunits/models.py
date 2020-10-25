"""
Copyright 2020 ООО «Верме»
"""

from django.db import models
from django.db.models import Q
from django.db.models.expressions import RawSQL


class OrganizationQuerySet(models.QuerySet):

    def get_children_filters(self, root_org_id):
        filters = Q(id=root_org_id)
        for c in self.filter(parent__id=root_org_id):
            _r = self.get_children_filters(c.id)
            if _r:
                filters |= _r
        return filters

    def get_parents_filters(self, child_org_id):
        filters = Q(id=child_org_id)
        for c in self.filter(child__id=child_org_id):
            _r = self.get_parents_filters(c.id)
            if _r:
                filters |= _r
        return filters

    def tree_downwards(self, root_org_id):
        """
        Возвращает корневую организацию с запрашиваемым root_org_id и всех её детей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type root_org_id: int
        """
        return self.filter(self.get_children_filters(root_org_id))

    def tree_upwards(self, child_org_id):
        """
        Возвращает корневую организацию с запрашиваемым child_org_id и всех её родителей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type child_org_id: int
        """

        return self.filter(self.get_parents_filters(child_org_id))


class Organization(models.Model):
    """ Организаци """

    objects = OrganizationQuerySet.as_manager()

    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name="Название")
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name="Код")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, verbose_name="Вышестоящая организация",
        related_name="child")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Организация"
        verbose_name = "Организации"

    def parents(self):
        """
        Возвращает всех родителей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_upwards()

        :rtype: django.db.models.QuerySet
        """

        return Organization.objects.tree_upwards(self.id).exclude(id=self.id)

    def children(self):
        """
        Возвращает всех детей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_downwards()

        :rtype: django.db.models.QuerySet
        """

        return Organization.objects.tree_downwards(self.id).exclude(id=self.id)

    def __str__(self):
        return self.name
