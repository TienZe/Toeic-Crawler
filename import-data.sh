
docker exec -i mysql_db mysql -uroot -proot toeic_booster < Voca/Vocaset/insert_collections.sql
docker exec -i mysql_db mysql -uroot -proot toeic_booster < Voca/Vocaset/insert_collection_tag.sql

docker exec -i mysql_db mysql -uroot -proot toeic_booster < Voca/Lesson/insert_lessons.sql
docker exec -i mysql_db mysql -uroot -proot toeic_booster < Voca/Word/insert_vocabularies.sql

docker exec -i mysql_db mysql -uroot -proot toeic_booster < Voca/Word/insert_lesson_vocabularies.sql



