# Трекер дел 

## Описание проекта

Основная идея программы включает в себя возможности приложений для ведения списков дел (todo list), календарей и трекеров задач с рядом изменений, расширений и уточнений.
		

##  Аналоги

Чтобы иметь представление о будущей программе, был рассмотрен ряд аналогичных программ, проведено их сравнение, выделены их преимущества и недостатки. 

### Списки дел
Предназначены для ведения списка личных дел, с дополнительными пометками.

Рассмотрено три приложения:

- **Wunderlist**
- **Todoist**
- **Any.do**

Возможности третьего, в отличие от первых двух не имеют каких-либо примечательных особенностей(по крайне мере в бесплатной версии). Поэтому далее, будут рассмотрены только **Wunderlist**, и **Todoist**. Ниже представлены возможности, которые присутствует в обоих приложениях. Речь идет только о бесплатных версиях.

Базовые возможности обоих программ:

- Создание задач, подзадач.
- Группировка задач в списки.
- Установка сроков выполнения
- Редактирование и удаление задач.
- Список "избранное".
- Поиск задач.
- Делегирование задачи.
- Наличие уведомлений.
- Сортировка задач по параметру.
- Повторяющиеся задачи.

Далее выделены их преимущества относительно друг друга.

#### Wunderlist 
 Преимущества:
 
- Широкий функционал в бесплатной версии.
- Набор стандартных списков. 
- Группировка списков в папки.
- Восстановление задач.
- Поиск задачи по подзадаче.
- Возможность добавить комментарий,  прикрепить изображение и др. файлы. 
- Возможность просмотра фактической даты выполнения.

Недостатки:

- Система приоритетов задач, основанная на разности между дедлайном и текущим временем. 
- Отсутствие реакции по прошествию дедлайна.

#### Todoist
Преимущества:

- Приоритизация задач на основе папок.
- Система достижений.  
- Событие при просрочке задачи.

Недостатки:

- Функционал бесплатной версии

Полезные возможности рассмотренных программ:

- Стандартные списки.
- Приоритизация задач на основе разделения списков.
- Событие после дедлайна.
- Возможность установки заметок.
- Восстановление выполненных задач.

### Календари

Предназначены для установки событий, связанных с определенными промежутками времени.

#### Google calendar

Преимущества и возможности:

- Настройка отображения календаря.
- События вида "мероприятие" и "напоминание"
- Возможность указать место, где будет проходить событие.
- Несколько уведомлений на событие.
- Статус события
- Возможность делится календарем.
- Можно пригласить "гостей" на мероприятие.
- Гости имеют возможность управлять мероприятием при наличии выданных прав.
- Поиск по параметрам.
- Корзина.
- Напоминание можно создать только в отдельном календаре.

Недостатки:

- Необходимость предварительной настройки.

Полезные возможности:

- Уведомления на событие.
- Статус события.
- Доступа к публичным календарям.
- Корзина

###  Трекеры задач

В общем виде служат для отслеживания выполнения задач в группах людей с иерархической системой управления.  Основная область применения - в разработке ПО и в IT в целом.

Хороший способ отслеживания существующих проблем, способ представления будущих улучшений.

#### Github Tracker (Issues)


Преимущества и возможности:

- Простота использования
- Возможность комментирование проблем
- Возможность оценивания проблемы и комментариев.
- Возможность подписки на конкретную проблему.
- Фильтры для поиска.
- Метки
- Делегирование проблем
- Наличие связей между проблемами.
- При коммитах есть возможность сослаться на проблему. 
Коммиты с префиксом Closed, Close, Fixed, Fix и тд. закроют проблему. 

#### Jira

Преимущества и возможности:

- Создание нескольких проектов
- Возможность назначить решение проблемы конкретному человеку.
- Возможность комментирования
- Можно выставить приоритет проблемы
- Несколько типов проблем: "подзадачи", "ошибки", "история"
- Можно выставить текущий статус "готово", "в работе", "сделать"
- Логирование времени (сколько потрачено, осталось, дата началы, описание проделанной работы) 
- Инструменты для создания отчетов

## Возможные сценарии использования

Цель программы - помочь отдельным личностям грамотно подойти к планированию времени, группам людей - к планированию и распределению обязаностей. 

- Ежедневные, повторяющиеся дела, на время пока они не вошли в привычку. Например, создать цель "Ходить на пробежку".
Поставить напоминание(я) за время до события.
Не выполненное задание помечается как проваленное.
- Добавить напоминание о необходимости поздравить коллегу с днем рождения.
- Совместные задачи и распределение подзадач.
	Написание совместного курсового проекта.
	Задача разбивается на подзадачи:
	 - работа с базой данных
	 - работа с бизнес-логикой
	 - работа с представлением	 
        Каждый участник проекта выбирает задачу.
	По завершению всех подзадач, главная задача считается законченной.
- Делегирование задач подчиненным. К примеру есть какой-то известный баг, просматривается список подчиненных, свободному назначается данная задача.

## Планируемые возможности программы

- CRUD операции над задачами и событиями.
- Объединение задач в папки (списки) по тематике, времени
- Создание вложенных задач.
- Стандартный набор папок:
	- Сегодня
	- Неделя
	- Выполненные
	- Избранное
- Создание проектов для совместных задач и событий.
- Делегирование задач в рамках проекта.
- Возможность выставить статус задачи
- Приоритезация личных задач, задач в рамках проекта.
- Создание блокирующих задач
- Создание повторяющихся задач и событий
- Возможность выставить статус задачи. 
- Комментирование задачи \ события.
- Создание меток
- Календарь для визуального отображения событий и задач.

## Логическая архитектура

Сущности:

User:

- UserID
- UserName
- PasswordHash
- PasswordSalt 
- Email

Event:

- EventID
- EventName
- UserID

Task:

- TaskID
- TaskName
- Description
- OwnerID
- ParentTaskID
- GroupID
- Status
- AssignedUserID
- StartDate
- EndDate

Folder:

- FolderID
- FolderName
- UserID


Notification:

- NotificationID
- EventID
- TaskID
- Date

Group:

- GroupID
- GroupName
- OwnerID

Cyclicity:

- CyclicityID
- TaskID
- EventID
- Period
- Duration


Comment:

- CommentID
- TaskID
- EventID
- UserID
- CreateDate
- Text

UserGroups:

- UserID
- GroupID

FolderTaskEvents:

- FolderID
- TaskID
- EventID




Класс User будет представлять конкретного пользователя. 

Задачи (Tasks) и события (Events) будут группироваться в папки (Folders). У пользователя будет набор стандартных папок. (сегодня, неделя, месяц, назначенные, удаленные, выполненные, избранное) Пользователь сможет создать собственные папки, в зависимости от его пожеланий.

У пользователя будет набор определенных групп, в которых он состоит. Для просмотра задач и событий группы нужно будет перейти в меню "Группы", выбрать конкретную группу из списка.

Для создания задачи или события, пользователю необходимо ввести название, опционально описание и напоминания, установить и настроить подзадачи. При необходимости пользователь сможет добавить "цикличность", для периодического появления события или задачи.
Статус задач будет выставляться автоматически в зависимости от дейстий пользователя. При выполнении задания, задаче будет выставлен статус "выполнена" при удалении - "удалена", в зависимости от этого задача отправится или в папку "выполненные" или "удаленные

Напоминания будут опционально применяться к задаче или событию. Напоминание будет состоять из даты, на которое оно назначено.

После создания группы пользователь может пригласить других пользователей, может создать необходимый набор заданий и событий. Распределить задачи между пользователями. (для этого у задачи предусмотрено соответствующее поле) 


## Этапы разработки

Рабочий прототип:

- Консольный интерфейс
- Хранение данных в базе данных SQLite
- Поддержка основных операции над задачи и событиями (без вложенных задач)
- Поиск задач
- Создание папок (списков задач)
- Настройка уведомлений

Основная версия: 

- Вложенные подзадачи для задач
- Циклические задачи и события.
- Переход к многопользовательскому приложению
- Операции над группами
- Расширение операций над задачами, необходимых для работы групп.

Финальная версия:

- Веб-интерфейс
- Комментарии
- Сортировка

Дополнительно хотелось бы реализовать:

- Метки
- Уведомления на почту
- Систему ролей для групп
- Комментирование задач вне группы.
- Статистику выполненных заданий за промежуток времени

## Сроки

- Прототип - до конца апреля
- Основная версия - до конца мая
- Финальная версия - до  сессии 

## Статус

В стадии проектирования.

