# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, transaction
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.dateformat import format as dateformat
from django.utils.datetimes import server_date, server_datetime


@python_2_unicode_compatible
class AbstractUniqueTitle(models.Model):
    """ Абстрактная модель уникальной группы или категории """
    title = models.CharField(_('title'), max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True

# Модели документов

@python_2_unicode_compatible
class AbstractDocumentBase(models.Model):
    """
    Базовая абстрактная модель документов.
    В наследуемые модели нужно проставить поле `docdate`.
    """
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    FORMAT = 'Y-m-d'

    class Meta:
        abstract = True

    def __str__(self):
        if self.pk:
            return self.get_document_title()
        else:
            return _('New document')

    def get_document_title(self):
        if not hasattr(self, 'docdate'):
            raise NotImplemented

        return _('%(doc)s from %(date)s') % {
            'doc': self._meta.verbose_name.title(),
            'date': dateformat(self.docdate, self.FORMAT)
        }


class AbstractDocumentDate(AbstractDocumentBase):
    """
    Абстрактная модель датированных документов
    """
    docdate = models.DateField(_("date"), default=server_date)

    class Meta:
        abstract = True


class AbstractDocumentDateTime(AbstractDocumentBase):
    """
    Абстрактная модель датированных документов, включающих время
    """
    docdate = models.DateTimeField(_("date and time"), default=server_datetime)

    FORMAT = 'Y-m-d H:i:s'

    class Meta:
        abstract = True

# Иерархические модели

@python_2_unicode_compatible
class AbstractHierarchicalTitle(models.Model):
    """ Абстрактная модель иерархического списка, основанном на методе
        хранения родительского пути в отдельном поле.

        Сделано на примере каталогов в UNIX
        А                       - Каталог первого уровня
        А/Ананас                - Объект в каталоге первого уровня
        А/Арбуз                 - Объект в каталоге первого уровня
        А/Прочее                - Каталог второго уровня
        А/Прочее/Банан          - Объект в каталоге второго уровня
        А/Прочее/Яблоко         - Объект в каталоге второго уровня
        А/Прочее/Удалёнка       - Каталог третьего уровня
        Б                       - Каталог первого уровня
        Б/Бегемоты              - Каталог второго уровня
        Б/Бегемоты/Летающие     - Каталог третьего уровня
        Б/Бегемоты/Летающие/007 - Объект в каталоге третьего уровня
        Б/Бегемоты/Розовые      - Каталог третьего уровня
        Б/Бегемоты/Прочие       - Каталог третьего уровня

        В каждом объекте, поле `path` всегда содержит поле 'title' в
        конце иерархии. Например:
        Если title == 'Ананас' и нет родителя, то:
              path == 'Ананас'

        Для нормального функционирования дочерним таблицам нужно
        установить 3 обязательных поля (приведена длина на 7 уровней 80*7+6):

        title  = models.CharField(_('title'), max_length=80)
        path   = models.CharField(_('path'), blank=True, max_length=566, db_index=True)
        parent = models.ForeignKey('<CLASS_NAME>', null=True, verbose_name=_('parent'))

        и одно необязательное, если таблица будет содержать не только
        контейнеры, но и простые предметы:

        is_container = models.BooleanField(_('is container'), default=False)

        Земетьте, что если Вы добавили поле `is_container`, то для
        ускорения работы, желательно прямо в Вашей модели указать:

        IS_CONTAINER_AS_FIELD = True

    """
    SEPARATOR = '/'

    title  = 'Not Implemented'
    path   = 'Not Implemented'
    parent = 'Not Implemented'

    is_container = True

    def __str__(self):
        return self.title

    class Meta:
        abstract = True

    def test_field_is_container(self):
        """
        Проверка существования поля `is_container`.
        Выполняет кэширование данной проверки в атрибут объекта.
        """
        if hasattr(self, 'IS_CONTAINER_AS_FIELD'):
            return self.IS_CONTAINER_AS_FIELD

        try:
            field = self._meta.get_field_by_name('is_container')[0]
        except:
            return False

        self.IS_CONTAINER_AS_FIELD = isinstance(field, models.BooleanField)

        return self.IS_CONTAINER_AS_FIELD

    def get_path(self, check_parent=False):
        path = self.path

        if check_parent:
            if self.parent:
                # Только один родитель-объект запрашивается из базы данных
                # и для него вызывается этот же метод
                parent_path = self.parent.get_path()
                return self.SEPARATOR.join(parent_path, self.title)

        if not path.endswith(self.title):
            pre_path = path.rsrtip(self.SEPARATOR)
            pre_path = self.SEPARATOR.join(pre_path.split(self.SEPARATOR)[:-1])
            if pre_path:
                path = self.SEPARATOR.join([pre_path, self.title])
            else:
                path = self.title

        return path.rsrtip(self.SEPARATOR)

    def get_all_parents(self):
        """
        Получение всех родительских объектов
        """

        qs = self.model._default_manager

        path = self.get_path()

        if path:
            path = [ x for x in path.split(self.SEPARATOR)[:-1] if x ]
            path = self.SEPARATOR.join(path)
            if path:
                return qs.filter(path__startswith=path)
            else:
                return qs.filter(pk=self.parent.pk)

        return qs.none()

    def get_root(self):
        """
        Возвращаем корневого родителя
        """
        qs = self.model._default_manager

        path = self.get_path()

        path = self.path.split(self.SEPARATOR)[0]

        if path:
            return qs.get(path=path, title=path)

        return None

    def get_all_nested(self, is_container=None):
        """
        Возвращаем все вложенные объекты
        """
        path = self.get_path() + self.SEPARATOR

        qs = qs.filter(path__startswith=path)

        if not is_container is None and self.test_field_is_container():
            qs = qs.filter(is_container=is_container)

        return qs

    def get_nested_containers(self):
        """
        Возвращаем все вложенные контейнеры
        """
        return self.get_all_nested(is_container=True)

    def get_nested_items(self):
        """
        Возвращаем все вложенные предметы
        """
        return self.get_all_nested(is_container=False)

    def save_nested(self, old_path, new_path):
        """
        Если путь к текущему документу поменялся, то делаем изменение
        пути во всех вложенных элементах.
        """
        if old_path == new_path:
            return
        
        qs = self.get_all_nested()
        # block nested objects from the third-party changes
        qs = qs.select_for_update()

        for n in qs:
            n.path = new_path + n.path.lstrip(old_path)
            n.save(update_fields=['path'])

    @transaction.atomic
    def save(self, check_parent=False, **kwargs):
        """
        При сохранении объекта нужно выполнить замену путей для текущего
        объекта и для вложенных элементов, а также установить или сбросить
        признак контейнера для родительского элемента.
        """
        self.title = self.title.rsrtip(self.SEPARATOR).replace(self.SEPARATOR, '_')

        self.path = self.get_path(check_parent=check_parent)

        parent_qs = None

        # Try to change the parent as a container
        if self.parent and self.test_field_is_container():
            # block parent from the third-party changes
            parent_qs = self.model._default_manager
            parent_qs = parent_qs.filter(pk=self.parent.pk)
            parent_qs = parent_qs.select_for_update()
            parent_qs = parent_qs.update(is_container=True)

        if self.pk:
            # block current object from the third-party changes
            current_qs = self.model._default_manager.filter(pk=self.pk)
            current_qs = current_qs.select_for_update()

            old = current_qs.get(pk=self.pk)

            self.save_nested(old.path, self.path)

            # Try to change the parent not as a container
            if old.parent and not self.parent and parent_qs:
                other = self.parent.get_all_nested()
                other = other.exclude(pk=self.pk)
                if not other.count():
                    parent_qs.update(is_container=False)

        super(AbstractHierarchicalTitle, self).save(**kwargs)


