CREATE TABLE hr.employee (
	emp_id serial4 NOT NULL,
	"name" varchar(100) NOT NULL,
	salary numeric(12, 2) NULL,
	designation varchar(100) NULL,
	department varchar(100) NULL,
	CONSTRAINT employee_pkey PRIMARY KEY (emp_id)
);

INSERT INTO hr.employee
(emp_id, "name", salary, designation, department, changed_by, reason, changed_time)
VALUES(2, 'Bob Smith', 1010.00, 'Senior Engineer', 'IT', 'Soumya', 'Promotion', '2025-05-06 12:12:07.957');
INSERT INTO hr.employee
(emp_id, "name", salary, designation, department, changed_by, reason, changed_time)
VALUES(3, 'Carol White', 10301.00, 'HR Specialist X', 'HR', 'aaff', 'Annual Review', '2025-05-06 12:12:21.715');
INSERT INTO hr.employee
(emp_id, "name", salary, designation, department, changed_by, reason, changed_time)
VALUES(1, 'Alice Johnson', 1005.00, 'Software Engineer', 'IT', 'Soumya', 'Correction', '2025-05-07 11:30:50.227');