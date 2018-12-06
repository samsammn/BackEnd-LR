
CREATE OR REPLACE FUNCTION getTweetUser(idUsers int)
RETURNS TABLE(
		iduser int,
        username text,
        fullname text,
        email text,
        photoprofile text,
        idtweet int,
		tweet text,
        media_image text,
        media_video text,
        tgl text
)
AS $$
BEGIN 
	RETURN QUERY select users.id as idUser, users.username as username, users.fullname as fullname, users.email as email, users.photoprofile as photoprofile, 
    	tweet.id as idTweet, tweet.tweet as tweet, tweet.media_image as media_image, 
        tweet.media_video as media_video, 
        tweet.tgl as tgl from users inner join tweet on users.id=tweet.id_user where users.id=idUsers;
END; $$

LANGUAGE 'plpgsql';


--- create function SignIn / Login
CREATE OR REPLACE FUNCTION signIn(sid int, pwd text)
RETURNS TABLE(
    staffId int,
    staffName text,
    emailStaff text,
    passwordStaff text,
    supervisorId text,
    gender text,
    divisionId text,
    locationUser text,
    staffLevel text,
    joinedDate text,
    tokenStaff text
)
AS $$
BEGIN
    RETURN QUERY SELECT staff_id as staffId, staff_name as staffName , email as emailStaff, password as passwordStaff, supervisor_id as supervisorId, sex as gender,
    division_id as divisionId, location_user as locationUser, staff_level as staffLevel, joined_date as joinedDate, token as tokenStaff from employee where staff_id = sid and password = pwd;
END; $$

LANGUAGE 'plpgsql';


--- Function get leave type
CREATE OR REPLACE FUNCTION getLeaveType()
RETURNS TABLE(
    id_leave int,
    leaveName text,
    entitlements int
)
AS $$
BEGIN
    RETURN QUERY Select id as id_leave, leave_name as leaveName, entitlement as entitlements from leave Order by leave_name Asc;
END; $$

LANGUAGE 'plpgsql'

--- Function get leave type by id leave type
CREATE OR REPLACE FUNCTION getLeaveTypeBy(idlt int)
RETURNS TABLE(
    id_leave int,
    leaveName text,
    typeLeave text,
    entitlements int
)
AS $$
BEGIN
    RETURN QUERY Select id as id_leave, leave_name as leaveName, type as typeLeave, entitlement as entitlements from leave where id=idlt Order by leave_name Asc;
END; $$

LANGUAGE 'plpgsql'

--- function get data Employee
CREATE or REPLACE FUNCTION getDataEmployee(sid int)
RETURNS TABLE(
    staffId int,
    staffName text,
    emailStaff text,
    passwordStaff text,
    supervisorId text,
    gender text,
    divisionId text,
    locationUser text,
    staffLevel text,
    joinedDate text,
    tokenStaff text
)
AS $$
BEGIN
    RETURN QUERY SELECT staff_id as staffId, staff_name as staffName , email as emailStaff, password as passwordStaff, supervisor_id as supervisorId, sex as gender,
    division_id as divisionId, location_user as locationUser, staff_level as staffLevel, joined_date as joinedDate, token as tokenStaff from employee where staff_id = sid;
END; $$

LANGUAGE 'plpgsql';

--- funstion submit To Supervisor
CREATE or REPLACE FUNCTION submitToSupervisor(sid int)
RETURNS TABLE(
    staffId int,
    staffName text,
    emailStaff text,
    passwordStaff text,
    supervisorId text,
    gender text,
    divisionId text,
    locationUser text,
    staffLevel text,
    joinedDate text,
    tokenStaff text
)
AS $$
BEGIN
    RETURN QUERY SELECT staff_id as staffId, staff_name as staffName , email as emailStaff, password as passwordStaff, supervisor_id as supervisorId, sex as gender,
    division_id as divisionId, location_user as locationUser, staff_level as staffLevel, joined_date as joinedDate, token as tokenStaff from employee where staff_id = sid;
END; $$

LANGUAGE 'plpgsql';


--- function insert Leave staff
select * from setLeaveStaff('20-05-2018','25-05-2018',0,'kagok hayang libur','25-05-2018','Approve', 'true', 'false','record:12345','bpmn:12345',2018112001)

CREATE OR REPLACE FUNCTION setLeaveStaff(start_dates text, end_dates text, leave_ids int, remarkss text, submission_dates text, statuss text, read_staffs text, read_supervisors text, record_ids text, process_ids text, staff_ids int)
RETURNS TABLE (
    startDate text,
    endDate text,
    leaveId int,
    remarksLeave text,
    submissionDate text,
    statusLeave text, 
    readStaff text,
    readSupervisor text,
    recordId text,
    processId text,
    staffId int
)
AS $$
BEGIN
insert into leave_detail (start_date, end_date, leave_id, remarks, submission_date, status, read_staff, read_supervisor, record_id, process_id, staff_id) values (start_dates, end_dates, leave_ids, remarkss, submission_dates, statuss, read_staffs, read_supervisors, record_ids, process_ids, staff_ids);
RETURN QUERY select start_date as startDate, end_date as endDate, leave_id as leaveId, remarks as remarksLeave, submission_date as submissionDate, status as statusLeave, read_staff as readStaff, read_supervisor as readSupervisor, record_id as recordId, process_id as processId, staff_id as staffId from leave_detail;
END; $$

LANGUAGE 'plpgsql';

---get Task list Supervisor
CREATE or REPLACE FUNCTION getTasklistSupervisor()
RETURNS TABLE(
    id_gettasklist int,
    startDate text,
    endDate text, 
    leaveId int,
    remarksStaff text,
    submissionDate text,
    statusLeave text,
    readStaff text,
    readSupervisor text,
    recordId text,
    processId text, 
    staffId int, 
    staffName text,
    emailStaff text,
    passwordStaff text,
    supervisorId text,
    gender text,
    divisionId text,
    locationUser text,
    staffLevel text,
    joinedDate text,
    tokenStaff text,
    leaveName text, 
    entitlementLeave int 
)
AS $$
BEGIN
RETURN QUERY select 
    leave_detail.id as id_gettasklist,
    leave_detail.start_date as startDate, 
    leave_detail.end_date as endDate, 
    leave_detail.leave_id as leaveId,
    leave_detail.remarks as remarksStaff, 
    leave_detail.submission_date as submissionDate,
    leave_detail.status as statusLeave,
    leave_detail.read_staff as readStaff,
    leave_detail.read_supervisor as readSupervisor,
    leave_detail.record_id as recordId,
    leave_detail.process_id as processId, 
    employee.staff_id as staffId,
    employee.staff_name as staffName,
    employee.email as emailStaff,
    employee.password as passwordStaff,
    employee.supervisor_id as supervisorId,
    employee.sex as gender,
    employee.division_id as divisionId,
    employee.location_user as locatioUser,
    employee.staff_level as staffLevel,
    employee.joined_date as joinedDate, 
    employee.token as tokenStaff, 
    leave.leave_name as leaveName, 
    leave.entitlement as entitlementLeave 
    from leave_detail inner join employee on leave_detail.staff_id=employee.staff_id inner join leave on leave_detail.leave_id=leave.id;
END; $$

LANGUAGE 'plpgsql';

---get Task list Staff
CREATE or REPLACE FUNCTION getTasklistSupervisor()
RETURNS TABLE(
    id_gettasklist int,
    startDate text,
    endDate text, 
    leaveId int,
    remarksStaff text,
    submissionDate text,
    statusLeave text,
    readStaff text,
    readSupervisor text,
    recordId text,
    processId text, 
    staffId int, 
    staffName text,
    emailStaff text,
    passwordStaff text,
    supervisorId text,
    gender text,
    divisionId text,
    locationUser text,
    staffLevel text,
    joinedDate text,
    tokenStaff text,
    leaveName text, 
    entitlementLeave int 
)
AS $$
BEGIN
RETURN QUERY select 
    leave_detail.id as id_gettasklist,
    leave_detail.start_date as startDate, 
    leave_detail.end_date as endDate, 
    leave_detail.leave_id as leaveId,
    leave_detail.remarks as remarksStaff, 
    leave_detail.submission_date as submissionDate,
    leave_detail.status as statusLeave,
    leave_detail.read_staff as readStaff,
    leave_detail.read_supervisor as readSupervisor,
    leave_detail.record_id as recordId,
    leave_detail.process_id as processId, 
    employee.staff_id as staffId,
    employee.staff_name as staffName,
    employee.email as emailStaff,
    employee.password as passwordStaff,
    employee.supervisor_id as supervisorId,
    employee.sex as gender,
    employee.division_id as divisionId,
    employee.location_user as locatioUser,
    employee.staff_level as staffLevel,
    employee.joined_date as joinedDate, 
    employee.token as tokenStaff, 
    leave.leave_name as leaveName, 
    leave.entitlement as entitlementLeave 
    from leave_detail inner join employee on leave_detail.staff_id=employee.staff_id inner join leave on leave_detail.leave_id=leave.id;
END; $$

LANGUAGE 'plpgsql';

---get Leave Detail
CREATE or REPLACE FUNCTION getLeaveDetail(lid int)
RETURNS TABLE(
    leaveId int,
    startDate text,
    endDate text, 
    remarksStaff text,
    submissionDate text,
    statusLeave text,
    readStaff text,
    readSupervisor text,
    recordId text,
    processId text, 
    staffId int, 
    staffName text,
    emailStaff text,
    passwordStaff text,
    supervisorId text,
    gender text,
    divisionId text,
    locationUser text,
    staffLevel text,
    joinedDate text,
    tokenStaff text,
    leaveName text, 
    entitlementLeave int 
)
AS $$
BEGIN
RETURN QUERY select 
    leave_detail.leave_id as leaveId,
    leave_detail.start_date as startDate, 
    leave_detail.end_date as endDate, 
    leave_detail.remarks as remarksStaff, 
    leave_detail.submission_date as submissionDate,
    leave_detail.status as statusLeave,
    leave_detail.read_staff as readStaff,
    leave_detail.read_supervisor as readSupervisor,
    leave_detail.record_id as recordId,
    leave_detail.process_id as processId, 
    employee.staff_id as staffId,
    employee.staff_name as staffName,
    employee.email as emailStaff,
    employee.password as passwordStaff,
    employee.supervisor_id as supervisorId,
    employee.sex as gender,
    employee.division_id as divisionId,
    employee.location_user as locatioUser,
    employee.staff_level as staffLevel,
    employee.joined_date as joinedDate, 
    employee.token as tokenStaff, 
    leave.leave_name as leaveName, 
    leave.entitlement as entitlementLeave 
    from leave_detail inner join employee on leave_detail.staff_id=employee.staff_id inner join leave on leave_detail.leave_id=leave.id where leave_detail.id=lid;
END; $$

LANGUAGE 'plpgsql';

-- Arima_lr@makersinstitute.id "N144ljs265EiUPDulcCqzFP2G_bUfzpCgcFZ2-rvT-o.aowif38yFJmd7NzBRm8AdNyhl1BjoQc5jCosTvZ4gIk"
-- Yamato_lr@makersinstitute.id "uSjMj_Ooo_ilHOBf5gqlkYvREp2Tf1mwYDfKNth460Q.25qLAoLg5R0LTJTNS6ZgubeKKSXiXDu9z74W4sMFvYc"
-- Tensi_lr@makersinstitute.id "wPmfG-oRIu7J7EVJ8N3duXNhBgN68iJ-WCx8cSFZ0Yk.1qmMi21VSnfaP4JLtsqpzMqeOkCXDzNi08gHWxhqYZo"