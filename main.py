import time, asyncio

from playwright.sync_api import ElementHandle

from inquiry_data import *
from playwright.async_api import async_playwright

async def search(page, user_data):
    """
    Searches if desired course has seats available. If available, calls registration function.
    :param page: takes as input a playwright page object
    :param user_data: takes as input a user data of object type Inquiry
    :return: returns 0 if no seats available, -1 if error, starts registration algorithm if seats found
    """

    await page.get_by_label("Search").fill("Search Class Schedule")
    await page.get_by_role("button", name="Go").click()
    await page.get_by_text("Step 2: Search Class Schedule and Add Course Sections").click()

    await page.locator("select").select_option(user_data.term)
    await page.get_by_role("button", name="Submit").click()

    # selects advances search
    await page.wait_for_url("https://horizon.mcgill.ca/pban1/bwckgens.p_proc_term_date")
    for i in range(15):
        await page.keyboard.press("Tab")
    await page.keyboard.press("Enter")

    #Selects faculty
    await page.wait_for_url("https://horizon.mcgill.ca/pban1/bwskfcls.P_GetCrse")
    for j in range(12):
        await page.keyboard.press("Tab")
    for element in user_data.faculty:
        await page.keyboard.press("Key" + element.upper())
    await page.screenshot(path="abc.png") #TODO fix this

    #Enters course number
    await page.get_by_test_id(test_id="crse_id").fill(user_data.course_num)
    await page.keyboard.press("Enter")

    #Reads and Parses Course Section Table
    response_type = 2
    await page.wait_for_selector("table", state="visible")
    rows = await page.query_selector_all("tr")

    begin = -1
    for row in rows:
        begin += 1
        check = await row.query_selector_all("td, th")

        if check:
            correct = await check[0].inner_text()
            if correct == "Select":
                break

    lecture_crn = None
    tutorial_crn = None

    for row in rows[begin + 1::3]:
        cells = await row.query_selector_all("td, th")
        section_num = await cells[4].inner_text()
        section_num = section_num.strip("0")

        left = await cells[12].inner_text()
        section_type = await cells[5].inner_text()

        if user_data.section == str(section_num) and int(left) != 0 and section_type == "Lecture":
            lecture_crn = await cells[1].inner_text()
            response_type = 1

        elif user_data.section == str(section_num) and section_type == "Lecture":
            response_type = 1
            break

        elif (section_type == "Tutorial" or section_type == "Laboratory") and int(left) != 0:
            tutorial_crn = await cells[1].inner_text()
            print(tutorial_crn)
            response_type = 0
            break

    if response_type == 0:
        await register(page, lecture_crn, tutorial_crn)

    return response_type



async def register(page, lecture_crn, tutorial_crn):
    """
    Registers for course based on course constants. Called by search function
    :param page: Takes as input a playwright page object
    :param lecture_crn: Lecture registration code
    :param tutorial_crn: Tutorial registration code
    :return: Nothing
    """

    #Navigate to Add/Drop Registration Portal
    await page.get_by_label("Search").fill("add/drop")
    await page.get_by_role("button", name="Go").click()
    await page.get_by_text("Quick Add or Drop Course Sections").click()

    for i in range(5):
        await page.mouse.wheel(0, 15000)
        time.sleep(0.05)

    await page.get_by_test_id(test_id="crn_id1").fill(lecture_crn)
    await page.get_by_test_id(test_id="crn_id2").fill(tutorial_crn)
    await page.get_by_role("button", name="Submit Changes").click()

async def query():
    begin = "Y" #input("Begin Minerva Registration Bot Setup? Y/N: ")

    if begin == "Y" or begin == "y":
        sid = input("Please enter your McGill student ID: ")
        pin = input("Please enter your PIN: ")
        term = input("Please enter your desired registration term (ex. Fall 2025): ")
        faculty = input("Please enter your course's faculty (ex. ECON): ")

        course_num = input("Please enter your course's faculty number (ex. 300 in FACC 300): ")
        section = input("Please enter your desired section number for this course (ex. 1 for 001): ")
        return Inquiry(sid, pin, term, faculty, course_num, section)

    else:
        print("Thank you for using Minerva Registration Bot.")
        return 0

async def main() -> None:
    async with async_playwright() as p:

        startup_sequence = [query()] #CHANGE-LOG - Moved further up so it works as a parallel sub-process
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://horizon.mcgill.ca/pban1/twbkwbis.P_WWWLogin")
        print(await page.title())

        startup_output = await asyncio.gather(*startup_sequence)
        user_data = startup_output[0] #Object of type Inquiry

        #Logs user into Minerva
        await page.get_by_label("McGill ID Number").fill(user_data.sid)
        await page.get_by_label("Minerva PIN").fill(user_data.pin)

        p.selectors.set_test_id_attribute("id")
        await page.get_by_test_id(test_id="mcg_id_submit").click()

        #Begin Searching for Open Seats and Registers if Available
        responses = ["Seats Available, Registering", "No Seats Available, Trying Again", "Error Seat Data Not Found"]
        status = await search(page, user_data)
        print(responses[status])
        total_elapsed = 0

        while status != 0:
            time.sleep(900)
            status = await search(page, user_data)
            print(responses[status])
            total_elapsed += 900

            if total_elapsed >= 10800:
                break #TODO fix this code

        #Ends program once registered
        await browser.close()

#Starts Program
asyncio.run(main())
