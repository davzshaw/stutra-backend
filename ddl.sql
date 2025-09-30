create table if not exists student (
    id varchar(36) primary key,
    name varchar(100) not null,
    lastname varchar(100) not null,
    birthday date not null
);

create table if not exists course (
    id integer primary key autoincrement,
    name varchar(100) not null,
    credits int not null
);

create table if not exists student_course (
    id integer primary key autoincrement,
    student_id varchar(36) not null,
    course_id integer not null,
    mark decimal(5,2),
    foreign key (student_id) references student(id) on delete cascade,
    foreign key (course_id) references course(id) on delete cascade
);