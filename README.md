## Кейс-задание

1. Миниприложение все написано в файле main.py, так как 30 мин слишком ограниченное время. Однако это не оптимальное решение.
2. Представляю более оптиальный вариант дерева приложения:  
![tree](https://github.com/andrzejabramov/buildin_quik/blob/master/img/project_tree.png)  
3. Так как не было задачи применять асинхронность, использованы синхронные функции, но можно исправить.
### 4. Проверяем работоспособность приложения. Тестируем Post запросы от пользователей:
- позитивный:  
```commandline
curl -X POST http://127.0.0.1:8000/reviews \
     -H "Content-Type: application/json" \
     -d '{"text": "Мне очень понравилось приложение! Быстро и удобно."}'
```
Ответ:  
```commandline
{
  "id": 1,
  "text": "Мне очень понравилось приложение! Быстро и удобно.",
  "sentiment": "positive",
  "created_at": "2025-04-05T15:30:00+00:00"
}
```  
![positive](https://github.com/andrzejabramov/buildin_quik/blob/master/img/queryPost_positive.png)  
- негативный:
```commandline
curl -X POST http://127.0.0.1:8000/reviews \
     -H "Content-Type: application/json" \
     -d '{"text": "Очень плохо работает. Всё лагает и крашится."}'
```  
Ответ:  
```commandline
{
  "id": 2,
  "text": "Очень плохо работает. Всё лагает и крашится.",
  "sentiment": "negative",
  "created_at": "2025-04-05T15:30:10+00:00"
}
```  
![negative](https://github.com/andrzejabramov/buildin_quik/blob/master/img/queryPost_negative.png)  
- нейтральный:
```commandline
curl -X POST http://127.0.0.1:8000/reviews \
     -H "Content-Type: application/json" \
     -d '{"text": "Приложение работает, но можно лучше."}'
```  
Ответ:  
```commandline
{
  "id": 3,
  "text": "Приложение работает, но можно лучше.",
  "sentiment": "neutral",
  "created_at": "2025-04-05T15:30:20+00:00"
}
```  
![neutral](https://github.com/andrzejabramov/buildin_quik/blob/master/img/queryPost_neutral.png)  
- пустое значение:  
```commandline
curl -X POST http://127.0.0.1:8000/reviews \
     -H "Content-Type: application/json" \
     -d '{"text": "   "}'
```  
ответ:    
```commandline
{
  "detail": "Поле 'text' не может быть пустым или состоять только из пробелов."
}
```  
![empty](https://github.com/andrzejabramov/buildin_quik/blob/master/img/queryPost_empty.png)   

### 5. Проверяем get запросы (ручка get): 
- все записи в БД:
```commandline
curl "http://127.0.0.1:8000/reviews"
```  
ответ:  
```commandline
[
  {
    "id": 3,
    "text": "Приложение работает, но можно лучше.",
    "sentiment": "neutral",
    "created_at": "2025-04-05T15:30:20+00:00"
  },
  {
    "id": 2,
    "text": "Очень плохо работает. Всё лагает и крашится.",
    "sentiment": "negative",
    "created_at": "2025-04-05T15:30:10+00:00"
  },
  {
    "id": 1,
    "text": "Мне очень понравилось приложение! Быстро и удобно.",
    "sentiment": "positive",
    "created_at": "2025-04-05T15:30:00+00:00"
  }
]
```
![all_feedbacks](https://github.com/andrzejabramov/buildin_quik/blob/master/img/get_all_feedback.png)  
- по фильтру (негатив к примеру):
```commandline
curl "http://127.0.0.1:8000/reviews?sentiment=negative"
```  
ответ:  
```commandline
[
  {
    "id": 2,
    "text": "Очень плохо работает. Всё лагает и крашится.",
    "sentiment": "negative",
    "created_at": "2025-04-05T15:30:10+00:00"
  }
]
```  
![any](https://github.com/andrzejabramov/buildin_quik/blob/master/img/get_any_feedback.png)  
- невалидное значение:  
```commandline
curl "http://127.0.0.1:8000/reviews?sentiment=any"  
```  
ответ:  
```commandline
{
  "detail": "sentiment должен быть одним из: positive, negative, neutral."
}
``` 
![invalid](https://github.com/andrzejabramov/buildin_quik/blob/master/img/get_invalid_feedback.png)
## 6. Зайдем в БД, проверим записи:  
![db](https://github.com/andrzejabramov/buildin_quik/blob/master/img/db_records.png)  

