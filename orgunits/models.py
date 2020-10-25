"""
Copyright 2020 ООО «Верме»
"""

from django.db import models
from django.db.models.expressions import RawSQL


class OrganizationQuerySet(models.QuerySet):

    def tree_downwards(self, root_org_id, include_self=True):
        """
        Возвращает корневую организацию с запрашиваемым root_org_id и всех её детей любого уровня вложенности
        :type root_org_id: int
        :type include_self: bool
        """
        table_name = self.model._meta.db_table
        query = (
            "WITH RECURSIVE child (id) AS ("
            f"  SELECT {table_name}.id FROM {table_name} WHERE id = {root_org_id}"
            "  UNION ALL"
            f"  SELECT {table_name}.id FROM child, {table_name}"
            f"  WHERE {table_name}.parent_id = child.id"
            ")"
            f" SELECT {table_name}.id"
            f" FROM {table_name}, child WHERE child.id = {table_name}.id"
        )
        if not include_self:
            query += f" AND {table_name}.id != {root_org_id}"
        return self.filter(id__in=RawSQL(query, []))

    def tree_upwards(self, child_org_id, include_self=True):
        """
        Возвращает корневую организацию с запрашиваемым child_org_id и всех её родителей любого уровня вложенности

        :type child_org_id: int
        :type include_self: bool
        """
        table_name = self.model._meta.db_table
        query = (
            "WITH RECURSIVE parent(id, parent_id) AS ("
            f"  SELECT {table_name}.id,{table_name}.parent_id FROM {table_name} WHERE id = {child_org_id}"
            "  UNION ALL"
            f"  SELECT {table_name}.id,{table_name}.parent_id FROM parent, {table_name}"
            f"  WHERE {table_name}.id = parent.parent_id"
            ")"
            f" SELECT {table_name}.id"
            f" FROM {table_name}, parent WHERE parent.id = {table_name}.id"
        )
        if not include_self:
            query += f" AND {table_name}.id != {child_org_id}"
        return self.filter(id__in=RawSQL(query, []))


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

        :rtype: django.db.models.QuerySet
        """
        return Organization.objects.tree_upwards(child_org_id=self.id, include_self=False)

    def children(self):
        """
        Возвращает всех детей любого уровня вложенности

        :rtype: django.db.models.QuerySet
        """

        return Organization.objects.tree_downwards(root_org_id=self.id, include_self=False)

    def __str__(self):
        return self.name
