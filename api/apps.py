from django.apps import AppConfig
# import requests
# import html5lib
# from bs4 import BeautifulSoup
import random

def startup():
    print("Hello world!")

    from .models import Timeslot, Room, College, Degree, Course, Faculty, CourseOffering, Section, Day, Building
    try:
        # Colleges
        ccs = College.objects.get_or_create(college_code='CCS', college_name='College of Computer Studies')
        cla = College.objects.get_or_create(college_code='CLA', college_name='College of Liberal Arts')
        cos = College.objects.get_or_create(college_code='COS', college_name='College of Science')
        gcoe = College.objects.get_or_create(college_code='GCOE', college_name='Gokongwei College of Engineering')
        soe = College.objects.get_or_create(college_code='SOE', college_name='School of Economics')
        bagced = College.objects.get_or_create(college_code='BAGCED', college_name='Br. Andrew Gonzalez College of Education')
        rvrcob = College.objects.get_or_create(college_code='RVRCOB', college_name='Ramon V. Del Rosario College of Business')
        # Degrees
        Degree.objects.get_or_create(degree_code='BS CS', degree_name='Bachelor of Science in Computer Science', college=ccs[0])
        Degree.objects.get_or_create(degree_code='BS IT', degree_name='Bachelor of Science in Information Technology', college=ccs[0])
        Degree.objects.get_or_create(degree_code='BS-PSY', degree_name='Bachelor of Science in Psychology', college=cla[0])
        Degree.objects.get_or_create(degree_code='AB-SOC', degree_name='Bachelor of Arts in Sociology', college=cla[0])
        Degree.objects.get_or_create(degree_code='AEI-BSA', degree_name='Bachelor of Science in Applied Economics, Major in Industrial Economics and Bachelor of Science in Accountancy', college=soe[0])
        Degree.objects.get_or_create(degree_code='AEI-ADV', degree_name='Bachelor of Science in Applied Economics, Major in Industrial Economics and Bachelor of Science in Advertising Management', college=soe[0])
        # Buildings
        goks = Building.objects.get_or_create(bldg_code='GK',bldg_name='Gokongwei Hall')
        lasalle = Building.objects.get_or_create(bldg_code='LS',bldg_name='St. La Salle Hall')
        yuch = Building.objects.get_or_create(bldg_code='Y',bldg_name='Enrique Yuchengco Hall')
        joseph = Building.objects.get_or_create(bldg_code='J',bldg_name='St. Joseph Hall')
        velasco = Building.objects.get_or_create(bldg_code='V',bldg_name='Velasco Hall')
        miguel = Building.objects.get_or_create(bldg_code='M',bldg_name='St. Miguel Hall')
        mutien = Building.objects.get_or_create(bldg_code='MU',bldg_name='St. Mutien Marie Hall')
        andrew = Building.objects.get_or_create(bldg_code='A',bldg_name='Br. Andrew Gonzales Hall')
        # Days
        monday = Day.objects.get_or_create(day_code='M', day_name='Monday')
        tuesday = Day.objects.get_or_create(day_code='T', day_name='Tuesday')
        wednesday = Day.objects.get_or_create(day_code='W', day_name='Wednesday')
        thursday = Day.objects.get_or_create(day_code='H', day_name='Thursday')
        friday = Day.objects.get_or_create(day_code='F', day_name='Friday')
        saturday = Day.objects.get_or_create(day_code='S', day_name='Saturday')
    except Exception as e:
        print(e)

    # def addCourseOffering(course):
    #     URL = "http://enroll.dlsu.edu.ph/dlsu/view_actual_count"
    #     PARAMS = {'p_course_code':course}
        
    #     try:
    #         r = requests.post(url = URL, params = PARAMS)
    #     except Exception as e:
    #         print(e)

    #     if(r.status_code == 200):
    #         parsed = BeautifulSoup(r.text, "html5lib").center
    #         rows = parsed.find_all("tr")
    #         for row in rows[1:]:
    #             rowData = row.get_text().strip().split("\n")
    #             if(len(rowData) == 1):
    #                 prof = rowData[0].strip()
    #                 Faculty(full_name=prof).save()
                    # for c in courseData[prevCourse[0]]:
                    #     if(not prof in c):
                    #         c.append(prof)
                    # if(not prof in courseProfs):
                    #     courseProfs[prof] = []
                    # if(not prevCourse[0] in courseProfs[prof]):
                    #     courseProfs[prof].append(prevCourse[0])
                # elif(len(rowData) == 3):
                #     print(rowData)
                    # newRowData = []
                    # for l in prevCourse:
                    #     newRowData.append(l)
                    # newRowData[3] = rowData[0]
                    # newRowData[4] = rowData[1]
                    # newRowData[5] = rowData[2]
                    # count = parseRow(newRowData, count)
                # elif(len(rowData) == 8):
                    # classnumber = rowData[0]
                    # course_code = rowData[1]
                    # section_code = rowData[2]
                    # days = rowData[3]
                    # timeslot = rowData[4]
                    # room = rowData[5]
                    # if(days.strip() != '' and timeslot.strip() != ''):
                    #     course = Course.objects.get(course_code=course_code)
                    #     section = Section.objects.get_or_create(section_code=section_code)
                    #     day1 = Day.objects.get(days.strip()[0])
                    #     day2 = Day.objects.get(days.strip()[1])

                    # count = parseRow(rowData, count)
                    # prevCourse = rowData
    # try:
    #     with open('course_codes.csv', 'r') as course_codes:
    #         for c in course_codes:
    #             Course(college=ccs, course_code=c.strip(), course_name='', course_desc='', units=3).save()
    #             addCourseOffering(c.strip())
    
    # except Exception as e:
    #     print(e)

    try:
        with open('ccs_offerings.tsv','r') as ccs_details:
            count = 1
            for l in ccs_details:
                details = l.split('\t')
                course_code = details[0].strip()
                section_code = 'S'+details[1].strip()
                faculty_name = '' 
                if(len(details[2].split('-')) == 3):
                    faculty_name = details[2].split('-')[0].strip()+'-'+details[2].split('-')[1].strip()+details[2].split('-')[2]
                elif(len(details[2].split('-')) == 2):
                    faculty_name = details[2].split('-')[0].strip()
                days = details[3].strip()
                time_begin = ''
                time_end= ''
                if(len(details[4].strip()) == 3):
                    time_begin = '0'+details[4][0]+':'+details[4][1]+details[4][2] 
                elif(len(details[4].strip()) == 4):
                    time_begin = details[4][0]+details[4][1]+':'+details[4][2]+details[4][3] 
                if(len(details[5].strip()) == 3):
                    time_end = '0'+details[5][0]+':'+details[5][1]+details[5][2] 
                elif(len(details[5].strip()) == 4):
                    time_end = details[5][0]+details[5][1]+':'+details[5][2]+details[5][3] 
                room_name = details[6].strip()
                for d in days:
                    classnumber = count
                    faculty = None
                    if(faculty_name != ''):
                        faculty = Faculty.objects.get_or_create(full_name=faculty_name)[0]
                    course = Course.objects.get_or_create(course_code=course_code, course_name='', course_desc='', college=ccs[0], units=3)[0]
                    section = Section.objects.get_or_create(section_code=section_code)[0]
                    day = Day.objects.get(day_code=d)
                    timeslot = Timeslot.objects.get_or_create(begin_time=time_begin, end_time=time_end)[0]
                    room = Room.objects.get_or_create(building=goks[0], room_name=room_name, room_type='', room_capacity=40)[0]
                    max_enrolled = random.randint(20,40)
                    current_enrolled = random.randint(0,40)
                    if(current_enrolled > max_enrolled):
                        current_enrolled = max_enrolled
                    status = True
                    CourseOffering.objects.get_or_create(classnumber=classnumber, faculty=faculty, course=course, section=section, day=day, timeslot=timeslot,room=room, current_enrolled=current_enrolled,max_enrolled=max_enrolled, status=status)
                count += 1
    except Exception as e:
        print(e)
        


class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = 'api'
    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):
            startup()
