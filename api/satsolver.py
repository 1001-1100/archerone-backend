import datetime
from z3 import *
from .models import CourseOffering, Course, Timeslot


def addHardConstraints(z3, highCourses, lowCourses, filterFull):
    allOfferings = CourseOffering.objects.none()
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
        for o in offerings:
            for o2 in offerings:
                if(o.section != o2.section):
                    a = Bool(str(o.classnumber))
                    b = Not(Bool(str(o2.classnumber)))
                    z3.add(Implies(a,b))
    for c in lowCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
        for o in offerings:
            for o2 in offerings:
                if(o.section != o2.section):
                    a = Bool(str(o.classnumber))
                    b = Not(Bool(str(o2.classnumber)))
                    z3.add(Implies(a,b))
    for o in allOfferings:
        if(filterFull):
            if(o.current_enrolled >= o.max_enrolled):
                a = Not(Bool(str(o.classnumber)))
                z3.add(a)
        for o2 in allOfferings:
            if(o.section != o2.section or o.course != o2.course):
                if(o.day == o2.day):
                    if(o.timeslot == o2.timeslot):
                        a = Bool(str(o.classnumber))
                        b = Not(Bool(str(o2.classnumber)))
                        z3.add(Implies(a,b))
                    else:
                        firstTime = o.timeslot
                        secondTime = o2.timeslot
                        if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))

def addSoftConstraints(z3, highCourses, lowCourses):
    currentPriority = 10 
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        for o in offerings:
            z3.add_soft(Bool(str(o.classnumber)), currentPriority) 
        currentPriority -= 0.1
    currentPriority = 2
    for c in lowCourses:
        offerings = CourseOffering.objects.filter(course=c)
        for o in offerings:
            z3.add_soft(Bool(str(o.classnumber)), currentPriority)
        currentPriority -= 0.01
    # for o in courseOfferings:
    #     a = Not(Bool(str(o['classNmbr'])))
    #     z3.add_soft(a, 10)

def addFriendConstraints(z3, mainCourses, diffCourses, sameCourses, mainUser, friends):

    mainOfferings = CourseOffering.objects.none()
    diffOfferings = CourseOffering.objects.none()
    sameOfferings = CourseOffering.objects.none()
    diffClassnumbers = []

    for c in mainCourses:
        offerings = CourseOffering.objects.filter(course=c)
        mainOfferings = mainOfferings | offerings

    for c in diffCourses:
        offerings = CourseOffering.objects.filter(course=c)
        for o in offerings:
            diffClassnumbers.append(o.classnumber)
        diffOfferings = diffOfferings | offerings

    for c in sameCourses:
        offerings = CourseOffering.objects.filter(course=c)
        sameOfferings = sameOfferings | offerings

    for o in sameOfferings:
        z3.add_soft(Bool(str(o.classnumber)))
    
    diffClassnumbers = list(set(diffClassnumbers))

    for c in mainUser['scheduleClasses']:
        if(c not in diffClassnumbers):
            z3.add_soft(Bool(str(c)))

    for o in mainOfferings:
        for o2 in diffOfferings:
            if(o.day == o2.day):
                if(o.timeslot == o2.timeslot):
                    a = Bool(str(o.classnumber))
                    b = Bool(str(o2.classnumber))
                    z3.add_soft(Implies(a,b),2)
                else:
                    firstTime = o.timeslot
                    secondTime = o2.timeslot
                    if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                        a = Bool(str(o.classnumber))
                        b = Bool(str(o2.classnumber))
                        z3.add_soft(Implies(a,b))
                    elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                        a = Bool(str(o.classnumber))
                        b = Bool(str(o2.classnumber))
                        z3.add_soft(Implies(a,b))
                    elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                        a = Bool(str(o.classnumber))
                        b = Bool(str(o2.classnumber))
                        z3.add_soft(Implies(a,b))

def addPreferences(z3, highCourses, lowCourses, preferences):
    allOfferings = CourseOffering.objects.none()
    otherPreferences = {}
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
    for c in lowCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
    for p in preferences:
        if(p.earliest_class_time != None):
            earliest = p.earliest_class_time
            for o in allOfferings:
                if(earliest > o.timeslot.begin_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))),2)
        if(p.latest_class_time != None):
            latest = p.latest_class_time
            for o in allOfferings:
                if(latest < o.timeslot.end_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))))
        if(p.preferred_days != None):
            day_id = p.preferred_days.id
            for o in allOfferings:
                if(day_id == o.day.id):
                    z3.add_soft(Bool(str(o.classnumber)))
        if(p.preferred_buildings != None):
            print(p.preferred_buildings)
        if(p.preferred_sections != None):
            section_code = p.preferred_sections
            for o in allOfferings:
                if(len(str(section_code)) == 1):
                    if(str(section_code)[0] == str(o.section.section_code)[0]):
                        z3.add_soft(Bool(str(o.classnumber)),2)
                else:
                    if(str(section_code) == str(o.section.section_code)):
                        z3.add_soft(Bool(str(o.classnumber)),2)
        if(p.preferred_faculty != None):
            faculty_id = p.preferred_faculty.id
            for o in allOfferings:
                if(o.faculty != None):
                    if(faculty_id == o.faculty.id):
                        z3.add_soft(Bool(str(o.classnumber)))
        if(p.min_courses != None):
            otherPreferences['min_courses'] = p.min_courses
        if(p.max_courses != None):
            otherPreferences['max_courses'] = p.max_courses
        if(p.undesirable_classes != None):
            classnumber = p.undesirable_classes
            z3.add(Not(Bool(str(classnumber))))
        # if(p.break_length != None):
        #     break_length = p.break_length
        #     for o in allOfferings:
        #         for o2 in allOfferings:
        #             if(o.section != o2.section or o.course != o2.course):
        #                 if(o.day == o2.day):
        #                     if(o.timeslot != o2.timeslot):
        #                         firstTime = o.timeslot
        #                         secondTime = o2.timeslot
        #                         if(firstTime.end_time < secondTime.begin_time):
        #                             firstEnd = datetime.datetime.combine(datetime.date.today(), firstTime.end_time)
        #                             secondBegin = datetime.datetime.combine(datetime.date.today(), secondTime.begin_time)
        #                             difference = (secondBegin - firstEnd).total_seconds() / 60
        #                             if(abs(difference - break_length) <= 60):
        #                                 a = Bool(str(o.classnumber))
        #                                 b = Bool(str(o2.classnumber))
                                        # z3.add(Implies(a,b))
                                        
def addFriendPreferences(z3, highCourses, preferences):
    allOfferings = CourseOffering.objects.none()
    otherPreferences = {}
    for c in highCourses:
        offerings = CourseOffering.objects.filter(course=c)
        allOfferings = allOfferings | offerings
    for p in preferences:
        if(p.earliest_class_time != None):
            earliest = p.earliest_class_time
            for o in allOfferings:
                if(earliest > o.timeslot.begin_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))))
        if(p.latest_class_time != None):
            latest = p.latest_class_time
            for o in allOfferings:
                if(latest < o.timeslot.end_time):
                    z3.add_soft(Not(Bool(str(o.classnumber))))
        if(p.preferred_days != None):
            day_id = p.preferred_days.id
            for o in allOfferings:
                if(day_id == o.day.id):
                    z3.add_soft(Bool(str(o.classnumber)))
        if(p.preferred_buildings != None):
            print(p.preferred_buildings)
        if(p.preferred_sections != None):
            section_code = p.preferred_sections
            for o in allOfferings:
                if(len(str(section_code)) == 1):
                    if(str(section_code)[0] == str(o.section.section_code)[0]):
                        z3.add_soft(Bool(str(o.classnumber)))
                else:
                    if(str(section_code) == str(o.section.section_code)):
                        z3.add_soft(Bool(str(o.classnumber)))
        if(p.preferred_faculty != None):
            faculty_id = p.preferred_faculty.id
            for o in allOfferings:
                if(o.faculty != None):
                    if(faculty_id == o.faculty.id):
                        z3.add_soft(Bool(str(o.classnumber)))
        if(p.min_courses != None):
            otherPreferences['min_courses'] = p.min_courses
        if(p.max_courses != None):
            otherPreferences['max_courses'] = p.max_courses
        if(p.undesirable_classes != None):
            classnumber = p.undesirable_classes
            z3.add_soft(Not(Bool(str(classnumber))), 10)
        # if(p.break_length != None):
        #     break_length = p.break_length
        #     for o in allOfferings:
        #         for o2 in allOfferings:
        #             if(o.section != o2.section or o.course != o2.course):
        #                 if(o.day == o2.day):
        #                     if(o.timeslot != o2.timeslot):
        #                         firstTime = o.timeslot
        #                         secondTime = o2.timeslot
        #                         if(firstTime.end_time < secondTime.begin_time):
        #                             firstEnd = datetime.datetime.combine(datetime.date.today(), firstTime.end_time)
        #                             secondBegin = datetime.datetime.combine(datetime.date.today(), secondTime.begin_time)
        #                             difference = (secondBegin - firstEnd).total_seconds() / 60
        #                             if(abs(difference - break_length) <= 60):
        #                                 a = Bool(str(o.classnumber))
        #                                 b = Bool(str(o2.classnumber))
                                        # z3.add(Implies(a,b))

    return otherPreferences

def checkPreferences(z3, model, preferences):
    unsatisfied = []
    offerings = None
    min_courses = None
    max_courses = None
    allOfferings = CourseOffering.objects.none()
    for o in model:
        if(model[o]):
            allOfferings = allOfferings | CourseOffering.objects.filter(classnumber=int(o.name()))
    days = []
    sections = []
    perDay = {
        'M': [],
        'T': [],
        'W': [],
        'H': [],
    }
    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            for d in perDay:
                for o in offerings:
                    if(o.day.day_code == d):
                        perDay[d].append(o)
            for p in preferences:
                if(p.earliest_class_time != None):
                    earliest = p.earliest_class_time
                    for o in offerings:
                        if(earliest > o.timeslot.begin_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts earlier than '+str(earliest))
                if(p.latest_class_time != None):
                    latest = p.latest_class_time
                    for o in offerings:
                        if(latest < o.timeslot.end_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts later than '+str(latest))
                if(p.preferred_days != None):
                    day = p.preferred_days.id
                    days.append(day)
                    # for o in offerings:
                    #     if(day_id != o.day.id):
                            # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day ('+str(p.preferred_days.day_code)+')')
                if(p.preferred_buildings != None):
                    pass
                if(p.preferred_sections != None):
                    section_code = p.preferred_sections
                    sections.append(section_code)
                    # for o in offerings:
                        # if(section_code not in o.section.section_code):
                            # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section ('+str(p.preferred_sections.section_code)+')')
                if(p.preferred_faculty != None):
                    faculty_id = p.preferred_faculty.id
                    for o in offerings:
                        if(o.faculty != None):
                            if(faculty_id != o.faculty.id):
                                pass
                                # unsatisfied.append('faculty')
                if(p.min_courses != None):
                    min_courses = p.min_courses
                if(p.max_courses != None):
                    max_courses = p.max_courses
                if(p.break_length != None):
                    break_length = p.break_length
    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            notSections = []
            for o in offerings:
                if(o.day.id not in days):
                    if(days != []):
                        unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day')
                sectionSatisfied = False
                for s in sections:
                    if(s in o.section.section_code):
                        sectionSatisfied = True
                if(not sectionSatisfied):
                    if(o.course.course_code not in notSections):
                        if(sections != []):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section')
                            notSections.append(o.course.course_code)

    if(min_courses != None):
        for d in perDay:
            if(int(min_courses) > len(perDay[d])):
                unsatisfied.append(str(d)+' has less than '+str(min_courses)+' courses')
    if(max_courses != None):
        for d in perDay:
            if(int(max_courses) < len(perDay[d])):
                unsatisfied.append(str(d)+' has more than '+str(max_courses)+' courses')
    return unsatisfied

def checkPreferencesFriends(offerings, preferences):
    z3 = Optimize()
    for o in offerings:
        z3.add(Bool(str(o.classnumber)))
    z3.check()
    model = z3.model()
    unsatisfied = []
    offerings = None
    min_courses = None
    max_courses = None
    allOfferings = CourseOffering.objects.none()
    for o in model:
        if(model[o]):
            allOfferings = allOfferings | CourseOffering.objects.filter(classnumber=int(o.name()))
    days = []
    sections = []
    perDay = {
        'M': [],
        'T': [],
        'W': [],
        'H': [],
    }
    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            for d in perDay:
                for o in offerings:
                    if(o.day.day_code == d):
                        perDay[d].append(o)
            for p in preferences:
                if(p.earliest_class_time != None):
                    earliest = p.earliest_class_time
                    for o in offerings:
                        if(earliest > o.timeslot.begin_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts earlier than '+str(earliest))
                if(p.latest_class_time != None):
                    latest = p.latest_class_time
                    for o in offerings:
                        if(latest < o.timeslot.end_time):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts later than '+str(latest))
                if(p.preferred_days != None):
                    day = p.preferred_days.id
                    days.append(day)
                    # for o in offerings:
                    #     if(day_id != o.day.id):
                            # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day ('+str(p.preferred_days.day_code)+')')
                if(p.preferred_buildings != None):
                    pass
                if(p.preferred_sections != None):
                    section_code = p.preferred_sections
                    sections.append(section_code)
                    # for o in offerings:
                        # if(section_code not in o.section.section_code):
                            # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section ('+str(p.preferred_sections.section_code)+')')
                if(p.preferred_faculty != None):
                    faculty_id = p.preferred_faculty.id
                    for o in offerings:
                        if(o.faculty != None):
                            if(faculty_id != o.faculty.id):
                                pass
                                # unsatisfied.append('faculty')
                if(p.min_courses != None):
                    min_courses = p.min_courses
                if(p.max_courses != None):
                    max_courses = p.max_courses
                if(p.break_length != None):
                    break_length = p.break_length

    for o in model:
        if(model[o]):
            offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
            notSections = []
            for o in offerings:
                if(o.day.id not in days):
                    if(days != []):
                        unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day')
                sectionSatisfied = False
                for s in sections:
                    if(s in o.section.section_code):
                        sectionSatisfied = True
                if(not sectionSatisfied):
                    if(o.course.course_code not in notSections):
                        if(sections != []):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section')
                            notSections.append(o.course.course_code)


    if(min_courses != None):
        for d in perDay:
            if(int(min_courses) > len(perDay[d])):
                unsatisfied.append(str(d)+' has less than '+str(min_courses)+' courses')
    if(max_courses != None):
        for d in perDay:
            if(int(max_courses) < len(perDay[d])):
                unsatisfied.append(str(d)+' has more than '+str(max_courses)+' courses')
    return unsatisfied

def checkPreferencesFriendsOther(offerings, mainCourses, friends):
    for friend in friends:
        friendCourses = friend['highCourses'] + friend['lowCourses']
        diffCourses = list(set(mainCourses) - set(friendCourses))
        chosenCourses = list(set(friendCourses) - set(diffCourses)) 
        newCourses = list(set(chosenCourses) - set(mainCourses))
        preferences = friend['preferences']
        z3 = Optimize()
        for o in offerings:
            if(o.course.id in chosenCourses):
                z3.add(Bool(str(o.classnumber)))
        friendOfferings = CourseOffering.objects.none()
        for c in newCourses:
            offerings = CourseOffering.objects.filter(course=c)
            friendOfferings = friendOfferings | offerings
        for o in friendOfferings:
            z3.add_soft(Bool(str(o.classnumber)))
        z3.check()
        model = z3.model()
        unsatisfied = []
        offerings = None
        min_courses = None
        max_courses = None
        allOfferings = CourseOffering.objects.none()
        for o in model:
            if(model[o]):
                allOfferings = allOfferings | CourseOffering.objects.filter(classnumber=int(o.name()))
        days = []
        sections = []
        classnumbers = []
        perDay = {
            'M': [],
            'T': [],
            'W': [],
            'H': [],
        }
        for o in model:
            if(model[o]):
                offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
                for d in perDay:
                    for o in offerings:
                        if(o.day.day_code == d):
                            perDay[d].append(o)
                for p in preferences:
                    if(p.earliest_class_time != None):
                        earliest = p.earliest_class_time
                        for o in offerings:
                            if(earliest > o.timeslot.begin_time):
                                unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts earlier than '+str(earliest))
                    if(p.latest_class_time != None):
                        latest = p.latest_class_time
                        for o in offerings:
                            if(latest < o.timeslot.end_time):
                                unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' starts later than '+str(latest))
                    if(p.preferred_days != None):
                        day = p.preferred_days.id
                        days.append(day)
                        # for o in offerings:
                        #     if(day_id != o.day.id):
                                # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day ('+str(p.preferred_days.day_code)+')')
                    if(p.preferred_buildings != None):
                        pass
                    if(p.preferred_sections != None):
                        section_code = p.preferred_sections
                        sections.append(section_code)
                        # for o in offerings:
                            # if(section_code not in o.section.section_code):
                                # unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section ('+str(p.preferred_sections.section_code)+')')
                    if(p.preferred_faculty != None):
                        faculty_id = p.preferred_faculty.id
                        for o in offerings:
                            if(o.faculty != None):
                                if(faculty_id != o.faculty.id):
                                    pass
                                    # unsatisfied.append('faculty')
                    if(p.min_courses != None):
                        min_courses = p.min_courses
                    if(p.max_courses != None):
                        max_courses = p.max_courses
                    if(p.break_length != None):
                        break_length = p.break_length
                    if(p.undesirable_classes != None):
                        classnumber = p.undesirable_classes
                        classnumbers.append(classnumber)

        for o in model:
            if(model[o]):
                offerings = CourseOffering.objects.filter(classnumber=int(o.name()))
                notSections = []
                notClass = []
                for o in offerings:
                    if(o.day.id not in days):
                        if(days != []):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not on a preferred day')
                    sectionSatisfied = False
                    for s in sections:
                        if(s in o.section.section_code):
                            sectionSatisfied = True
                    if(not sectionSatisfied):
                        if(o.course.course_code not in notSections):
                            if(sections != []):
                                unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' ('+o.day.day_code+')'+' is not a preferred section')
                                notSections.append(o.course.course_code)
                    if(o.classnumber in classnumbers):
                        if(o.course.course_code not in notClass):
                            unsatisfied.append(str(o.course.course_code)+' '+o.section.section_code+' is not a preferred class')
                            notClass.append(o.course.course_code)

        if(min_courses != None):
            for d in perDay:
                if(int(min_courses) > len(perDay[d])):
                    unsatisfied.append(str(d)+' has less than '+str(min_courses)+' courses')
        if(max_courses != None):
            for d in perDay:
                if(int(max_courses) < len(perDay[d])):
                    unsatisfied.append(str(d)+' has more than '+str(max_courses)+' courses')

        selectedCourses = []
        for o in allOfferings:
            if(o.course.id in chosenCourses):
                selectedCourses.append(o.course.course_code)
        selectedCourses = set(selectedCourses)
        allCourses = []
        for c in newCourses:
            allCourses.append(Course.objects.get(id=c).course_code)
            
        for c in allCourses:
            if not (c in selectedCourses):
                unsatisfied.append(c)



        return unsatisfied

def addExtraConstraints(z3, model):
    current = []
    for o in model:
        if(model[o]):
            current.append((Not(Bool(str(o)))))
    z3.add(Or(tuple(current)))

def addExtraConstraintsFriends(z3, offerings):
    current = []
    for o in offerings:
        current.append(Not(Bool(str(o.classnumber))))
    z3.add(Or(tuple(current)))

def search(courses, preferences):
    z3 = Optimize()

    # addHardConstraints(z3, courses, [], False, [])
    addSoftConstraints(z3, [], courses)
    otherPreferences = addPreferences(z3, courses, [], preferences)

    schedules = []

    z3.check()
    model = z3.model()
    offerings = CourseOffering.objects.none() 
    for o in model:
        if(model[o]):
            offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))

    return offerings

def solve(highCourses, lowCourses, preferences, filterFull):
    z3 = Optimize()

    addHardConstraints(z3, highCourses, lowCourses, filterFull)
    addSoftConstraints(z3, highCourses, lowCourses)
    otherPreferences = addPreferences(z3, highCourses, lowCourses, preferences)

    schedules = []

    for i in range(0, 10):
        z3.check()
        model = z3.model()
        schedule = {}
        information = []
        selectedCourses = []
        offerings = CourseOffering.objects.none() 
        for o in model:
            if(model[o]):
                offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))
        if(len(offerings) == 0):
            break
        for o in offerings:
            selectedCourses.append(o.course.course_code)
        selectedCourses = set(selectedCourses)
        allCourses = []
        for c in highCourses:
            allCourses.append(Course.objects.get(id=c).course_code)
        for c in lowCourses:
            allCourses.append(Course.objects.get(id=c).course_code)
            
        for c in allCourses:
            if not (c in selectedCourses):
                information.append(c)
            
        schedule['offerings'] = offerings
        schedule['information'] = set(information)
        schedule['preferences'] = checkPreferences(z3, model, preferences)
        print(schedule['information'])
        print(schedule['preferences'])
        schedules.append(schedule)

        addExtraConstraints(z3, model)
        addSoftConstraints(z3, highCourses, lowCourses)

    return schedules 

def solveFriends(mainUser, friends):
    z3 = Optimize()

    friendCourses = []
    mainCourses = mainUser['highCourses'] + mainUser['lowCourses']
    for f in friends:
        friendCourses += list(set(f['highCourses'] + f['lowCourses']))
        
    diffCourses = list(set(friendCourses) - set(mainCourses))
    sameCourses = list(set(mainCourses + friendCourses) - set(diffCourses))

    addFriendConstraints(z3, mainCourses, diffCourses, sameCourses, mainUser, friends)
    addHardConstraints(z3, mainUser['highCourses'], mainUser['lowCourses'], mainUser['filterFull'])
    addSoftConstraints(z3, mainUser['highCourses'], mainUser['lowCourses'])
    otherPreferences = addPreferences(z3, mainUser['highCourses'], mainUser['lowCourses'], mainUser['preferences'])

    for f in friends:
        otherPreferences = addPreferences(z3, sameCourses, sameCourses, f['preferences'])

    schedules = []

    for i in range(0, 10):
        z3.check()
        model = z3.model()
        schedule = {}
        information = []
        selectedCourses = []
        offerings = CourseOffering.objects.none() 
        for o in model:
            if(model[o]):
                offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))
        if(len(offerings) == 0):
            break
        newOfferings = []
        for o in offerings:
            if(o.course.id in mainUser['highCourses'] or o.course.id in mainUser['lowCourses']):
                newOfferings.append(o)
                selectedCourses.append(o.course.course_code)
        offerings = newOfferings
        selectedCourses = set(selectedCourses)
        allCourses = []
        for c in mainUser['highCourses']:
            allCourses.append(Course.objects.get(id=c).course_code)
        for c in mainUser['lowCourses']:
            allCourses.append(Course.objects.get(id=c).course_code)
            
        for c in allCourses:
            if not (c in selectedCourses):
                information.append(c)
            
        schedule['offerings'] = offerings
        schedule['information'] = set(information)
        schedule['preferences'] = checkPreferencesFriends(offerings, mainUser['preferences'])
        schedule['friendPreferences'] = checkPreferencesFriendsOther(offerings, mainCourses, friends)
        print(schedule['information'])
        print(schedule['preferences'])
        schedules.append(schedule)

        addExtraConstraintsFriends(z3, offerings)

        addSoftConstraints(z3, mainUser['highCourses'], mainUser['lowCourses'])
        for f in friends:
            addSoftConstraints(z3, f['highCourses'], f['lowCourses'])

    return schedules 

def solveEdit(classes, newclasses, courses):
    def addHardConstraints():
        allOfferings = CourseOffering.objects.none()
        for c in courses:
            offerings = CourseOffering.objects.filter(course=c)
            allOfferings = allOfferings | offerings
            for o in offerings:
                for o2 in offerings:
                    if(o.section != o2.section):
                        a = Bool(str(o.classnumber))
                        b = Not(Bool(str(o2.classnumber)))
                        z3.add(Implies(a,b))
        for o in allOfferings:
            for o2 in allOfferings:
                if(o.section != o2.section or o.course != o2.course):
                    if(o.day == o2.day):
                        if(o.timeslot == o2.timeslot):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        else:
                            firstTime = o.timeslot
                            secondTime = o2.timeslot
                            if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
        for c in newclasses:
            z3.add_soft(Bool(str(c)),10)
    def addSoftConstraints():
        for c in classes:
            z3.add_soft(Bool(str(c)))

    z3 = Optimize()

    addHardConstraints()
    addSoftConstraints()

    z3.check()
    model = z3.model()
    offerings = CourseOffering.objects.none() 
    print(model)
    print(classes)
    print(newclasses)
    print(courses)
    for o in model:
        if(model[o]):
            offerings = offerings | CourseOffering.objects.filter(classnumber=int(o.name()))

    schedule = {}
    allCourses = []
    selectedCourses = []
    selectedNumbers = []
    rejected = []

    for c in courses:
        allCourses.append(Course.objects.get(id=c).course_code)

    for o in offerings:
        selectedCourses.append(o.course.course_code)
        selectedNumbers.append(o.classnumber)
    selectedCourses = set(selectedCourses)

    for c in allCourses:
        if not (c in selectedCourses):
            rejected.append(c)
    
    print(schedule)
    print(selectedCourses)
    print(allCourses)

    schedule['offerings'] = offerings
    schedule['rejected'] = set(rejected)
    schedule['classnumbers'] = set(selectedNumbers)

    return schedule 

def checkConflicts(classnumbers):
    def addHardConstraints():
        allOfferings = CourseOffering.objects.none()
        for c in classnumbers:
            offerings = CourseOffering.objects.filter(classnumber=c)
            allOfferings = allOfferings | offerings
        for o in allOfferings:
            for o2 in allOfferings:
                if(o.section != o2.section or o.course != o2.course):
                    if(o.day == o2.day):
                        if(o.timeslot == o2.timeslot):
                            a = Bool(str(o.classnumber))
                            b = Not(Bool(str(o2.classnumber)))
                            z3.add(Implies(a,b))
                        else:
                            firstTime = o.timeslot
                            secondTime = o2.timeslot
                            if(firstTime.begin_time >= secondTime.begin_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.begin_time and firstTime.end_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
                            elif(firstTime.end_time >= secondTime.end_time and firstTime.begin_time <= secondTime.end_time):
                                a = Bool(str(o.classnumber))
                                b = Not(Bool(str(o2.classnumber)))
                                z3.add(Implies(a,b))
    def addClassnumbers():
        for c in classnumbers:
            z3.add(Bool(str(c)))

    z3 = Optimize()

    addHardConstraints()
    addClassnumbers()

    return z3.check()


# def start(inputCourses, inputProfs, inputNotSections, inputNotRooms, inputNotBefore, inputNotAfter, inputNotDays, inputCheckFull, num):

#     z3 = Optimize()

#     courses = []
#     courseData = {}
#     courseNames = {}
#     courseDays = {}
#     courseProfs = {}
#     prevCourse = None

#     def filters(z3):
#         return z3

#     def isFull(course):
#         if(inputCheckFull):
#             for c in course:
#                 if(int(c[6]) <= int(c[7])):
#                     return True
#         return False

#     def notTime(time):
#         for t in time:
#             t1 = t[4].split('-')
#             s1 = int(t1[0].strip())
#             e1 = int(t1[1].strip())
#             start1 = datetime.time(int(s1/100),s1%100,0,0)
#             end1 = datetime.time(int(e1/100),e1%100,0,0)
#             start2 = datetime.time(int(inputNotBefore/100),inputNotBefore%100,0,0)
#             end2 = datetime.time(int(inputNotAfter/100),inputNotAfter%100,0,0)
#             if(start1 < start2 or end1 < start2 or start1 > end2 or end1 > end2):
#                 return True
#         return False

#     def notDay(day):
#         if(inputNotDays != ""):
#             days = inputNotDays.split(",")
#             for d in days:
#                 if(day == d):
#                     return True
#         return False

#     def notSection(c):
#         if(inputNotSections != ""):
#             notSections = inputNotSections.split(",")
#             for section in notSections:
#                 for c2 in courseData[c]:
#                     if(section in c2[2]):
#                         return True
#         return False

#     def notRoom(c):
#         if(inputNotRooms != ""):
#             notRooms = inputNotRooms.split(",")
#             for room in notRooms:
#                 for c2 in courseData[c]:
#                     if(room in c2[5]):
#                         return True
#         return False

#     def hasProf(c):
#         profs = inputProfs.split(",")
#         for prof in profs:
#             for c2 in courseData[c]:
#                 for d in c2:
#                     if(prof in d):
#                         return True
#         return False

#     def profExists(course):
#         if(inputProfs != ""):
#             profs = inputProfs.split(",")
#             print(profs)
#             for prof in profs:
#                 for profName in courseProfs:
#                     if(prof in profName):
#                         for c in courseNames[course]:
#                             for c2 in courseData[c]:
#                                 for d in c2:
#                                     if(prof in d):
#                                         return True
#         return False

#     def parseRow(rowData, count):
#         days = list(rowData[3])
#         for day in days:
#             if(not day in courseDays):
#                 courseDays[day] = []
#             if(not rowData[0] in courseDays[day]):
#                 courseDays[day].append(rowData[0])
#         course = rowData[1].strip()
#         if(not course in courseNames):
#             courseNames[course] = []
#         if(not rowData[0] in courseNames[course]):
#             courseNames[course].append(rowData[0])
#         if(not rowData[0] in courseData):
#             courseData[rowData[0]] = []
#         courseData[rowData[0]].append(rowData)
#         return count

#     def compareTimes(course1,course2):
#         for c1 in course1:
#             for c2 in course2:
#                 t1 = c1[4].split('-')
#                 t2 = c2[4].split('-')
#                 s1 = int(t1[0].strip())
#                 e1 = int(t1[1].strip())
#                 s2 = int(t2[0].strip())
#                 e2 = int(t2[1].strip())
#                 start1 = datetime.time(int(s1/100),s1%100,0,0)
#                 end1 = datetime.time(int(e1/100),e1%100,0,0)
#                 start2 = datetime.time(int(s2/100),s2%100,0,0)
#                 end2 = datetime.time(int(e2/100),e2%100,0,0)
#                 if(start1 >= start2 and start1 <= end2):
#                     if(end1 >= start2 and end1 <= end2):
#                         return True
#         return False

#     inputCourses = inputCourses.split(",")
#     for course in inputCourses:
#         course = course.strip()
#         courses.append(course)

#     if(len(courses) > 0):
#         count = 0
#         for course in courses:
#             URL = "http://enroll.dlsu.edu.ph/dlsu/view_actual_count"
#             PARAMS = {'p_course_code':course}
#             print("Retrieving data for "+course+"...")
            
#             try:
#                 r = requests.post(url = URL, params = PARAMS)
#             except:
#                 return "Error encountered. Try again."

#             if(r.status_code == 200):
#                 parsed = BeautifulSoup(r.text, "html5lib").center
#                 rows = parsed.find_all("tr")
#                 for row in rows[1:]:
#                     rowData = row.get_text().strip().split("\n")
#                     if(len(rowData) == 1):
#                         prof = rowData[0].strip()
#                         for c in courseData[prevCourse[0]]:
#                             if(not prof in c):
#                                 c.append(prof)
#                         if(not prof in courseProfs):
#                             courseProfs[prof] = []
#                         if(not prevCourse[0] in courseProfs[prof]):
#                             courseProfs[prof].append(prevCourse[0])
#                     elif(len(rowData) == 3):
#                         newRowData = []
#                         for l in prevCourse:
#                             newRowData.append(l)
#                         newRowData[3] = rowData[0]
#                         newRowData[4] = rowData[1]
#                         newRowData[5] = rowData[2]
#                         count = parseRow(newRowData, count)
#                     elif(len(rowData) == 8):
#                         count = parseRow(rowData, count)
#                         prevCourse = rowData
#             else:
#                 print("Server unavailable.")
#                 break

#         # for c in courseData:
#         #     print(courseData[c])
#         # print(courseProfs)
#         # print(courseNames)
#         # print(courseDays)
#         print("Parsing data...")

#         for course in courseNames:
#             courseList = []
#             notCourseList = []
#             if(profExists(course)):
#                 for c in courseNames[course]:
#                     if(hasProf(c) and not notSection(c) and not notRoom(c)):
#                         courseList.append(Bool(c))
#                     else:
#                         notCourseList.append(Bool(c))
#             else:
#                 for c in courseNames[course]:
#                     if(not notSection(c) and not notRoom(c)):
#                         courseList.append(Bool(c))
#                     else:
#                         notCourseList.append(Bool(c))
#             z3.add_soft(Or(tuple(courseList)),1)
#             for c in notCourseList:
#                 z3.add(Not(Bool(str(c))))
#             for c in courseList:
#                 if(isFull(courseData[str(c)])):
#                     z3.add(Not(Bool(str(c))))
#                 else:
#                     otherCourseList = []
#                     for c2 in courseList:
#                         if(str(c) != str(c2)):
#                             otherCourseList.append(Not(Bool(str(c2))))
#                     z3.add(Implies(Bool(str(c)),And(tuple(otherCourseList))))

#         for day in courseDays:
#             if(notDay(day)):
#                 for c in courseDays[day]:
#                     z3.add(Not(Bool(c)))
#             else:
#                 for c in courseDays[day]:
#                     if(notTime(courseData[c])):
#                         z3.add(Not(Bool(c)))
#                     else:
#                         for c2 in courseDays[day]:
#                             if(c != c2):
#                                 if(compareTimes(courseData[c],courseData[c2])):
#                                     # if(not str(0-idMapping[c])+' '+str(0-idMapping[c2])+' 0\n' in dimacs):
#                                     z3.add(Or(Not(Bool(c)), Not(Bool(c2))))
        
#         z3 = filters(z3)

#         print(z3)
#         print("Calculating schedules...")

#         schedules = ""
#         preSolver = str(z3)
#         count = 0
#         while(str(z3.check()) == "sat" and count < num):
#             print()
#             courseList = []
#             for c in z3.model():
#                 if(is_true(z3.model()[c])):
#                     print(courseData[str(c)][0])
#                     schedules += str(courseData[str(c)][0])+"<br>"
#                     courseList.append(Not(Bool(str(c))))
#             schedules += "<br>"
#             print(courseList)
#             z3.add(Or(tuple(courseList)))
#             print()
#             # print(z3)
#             print(z3.check())
#             count += 1
#         schedules += "<br><br>Z3 Solver:<br>"
#         schedules += preSolver
#         print(z3)
        
#         print(count-1,"schedules found.")
#         print(num)

#         return schedules

#     else:
#         print("Nothing found.")