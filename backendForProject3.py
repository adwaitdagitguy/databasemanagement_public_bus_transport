from flask import Flask, render_template, request, redirect, url_for,flash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sql_21#AP'
app.config['MYSQL_DB'] = 'busmanagementsystem2'

mysql = MySQL(app)

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/passenger')
def passenger():
    return render_template('passenger.html')

@app.route('/staff')
def staff():
    return render_template('staff.html')

@app.route('/authority')
def authority():
    return render_template('authority.html')  # Add Bus form will be on this page

# Route to handle form submission for adding a bus
@app.route('/add_bus', methods=['POST'])
def add_bus():
    if request.method == 'POST':
        # Get bus details from the form
        bus_id = request.form['BusId']
        up_or_down = request.form['UpOrDown']
        bus_ferry_number = request.form['busFerryNumber']
        model = request.form['Model']
        capacity = request.form['Capacity']
        frequency_in_minutes = request.form['FrequencyInMinutes']
        reservation_percent = request.form['ReservationPercent']
        route_id = request.form['RouteID']
        first_bus = request.form['FirstBus']
        last_bus = request.form['LastBus']
        journey_status = request.form['journeyStatus']
        managing_group = request.form['ManagingGroup']
        depot_id = request.form['depotId']

        # Insert the new bus into the Bus table
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO Bus (BusId, UpOrDown, busFerryNumber, Model, Capacity, FrequencyInMinutes, 
                             ReservationPercent, RouteID, FirstBus, LastBus, journeyStatus, ManagingGroup, depotId) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (bus_id, up_or_down, bus_ferry_number, model, capacity, frequency_in_minutes, 
              reservation_percent, route_id, first_bus, last_bus, journey_status, managing_group, depot_id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('authority'))

@app.route('/feedback_from_passengers', methods=['GET'])
def feedback_from_passengers():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM feedbacksummary')  # Query the view
    data = cursor.fetchall()
    cursor.close() 
    return render_template('feedback_summary.html', feedback=data)

@app.route('/ticketing_data_analysis')
def ticketing_data_analysis():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM TicketSalesByRoute")
    ticket_sales = cursor.fetchall()
    cursor.close()
    return render_template('ticketing_data_analysis.html', ticket_sales=ticket_sales)

@app.route('/update_staff_details', methods=['GET', 'POST'])
def update_staff_details():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        new_salary = request.form['new_salary']
        
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE staff SET Salary = %s WHERE StaffID = %s", (new_salary, staff_id))
        mysql.connection.commit()
        cursor.close()
        return "Salary updated successfully!"
    return render_template('update_staff_details.html')

@app.route('/route_remove', methods=['GET', 'POST'])
def route_remove():
    if request.method == 'POST':
        route_id = request.form['route_id']
        
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM routes WHERE RouteID = %s", (route_id,))
        mysql.connection.commit()
        cursor.close()
        
        return "Route removed successfully!"
    return render_template('route_remove.html')

@app.route('/update_journey_status', methods=['GET', 'POST'])
def update_journey_status():
    if request.method == 'POST':
        bus_id = request.form['busId']
        journey_status = request.form['journeyStatus']
        
        # Check if both busId and journeyStatus are provided
        

        # Update the journey status of the bus in the database
        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE Bus
            SET journeyStatus = %s
            WHERE BusId = %s
        ''', (journey_status, bus_id))

        mysql.connection.commit()

        # Check if the update was successful
        cursor.close()

        return redirect(url_for('staff'))  # Redirect back to staff page after update
    return render_template('update_journey_status.html')  # Render form for updating journey status

@app.route('/insert_maintenance_record', methods=['GET', 'POST'])
def insert_maintenance_record():
    if request.method == 'POST':
        maintenance_id = request.form['maintenanceId']
        cost = request.form['cost']
        date_of_maintenance = request.form['dateOfRecentMaintenance']
        bus_condition = request.form['busCondition']
        bus_id = request.form['BusId']
        
        # Validate input
        if not maintenance_id or not cost or not date_of_maintenance or not bus_condition or not bus_id:
            return render_template('insert_maintenance_record.html', message="All fields are required")
        
        # Insert maintenance record into the database
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO MaintenanceRecords (maintenanceId, cost, dateOfRecentMaintenance, busCondition, BusId)
            VALUES (%s, %s, %s, %s, %s)
        ''', (maintenance_id, cost, date_of_maintenance, bus_condition, bus_id))
        
        mysql.connection.commit()
        cursor.close()

        return render_template('insert_maintenance_record.html', message="Maintenance record added successfully!")

    return render_template('insert_maintenance_record.html')  # Show the form for inserting maintenance record

@app.route('/read_ticketing_data', methods=['GET', 'POST'])
def read_ticketing_data():
    if request.method == 'POST':
        # Get inputs from the form
        bus_id = request.form['busID']
        date = request.form['date']

        cursor = mysql.connection.cursor()
        # Query tickets table for the specified busID and date
        query = '''
            SELECT * FROM tickets 
            WHERE busID = %s AND DATE(DateAndTime) = %s
        '''
        cursor.execute(query, (bus_id, date))
        tickets = cursor.fetchall()
        cursor.close()

        # Pass the queried data to the template
        return render_template('read_ticketing_data.html', tickets=tickets, bus_id=bus_id, date=date)

    # Render the form if the request method is GET
    return render_template('read_ticketing_data_form.html')

@app.route('/book_ticket', methods=['POST', 'GET'])
def book_ticket():
    if request.method == 'POST':
        # Collect data from the form
        ticket_type = request.form['ticketType']
        start_stop_name = request.form['startStopName']
        end_stop_name = request.form['endStopName']
        bus_id = request.form['busID']
        ticket_mode = request.form['ticketMode']
        route_id = request.form['routeID']

        # Insert into the database
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO tickets 
            (TicketType, StartStopName, EndStopName, busID, ticketMode, RouteId) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (ticket_type, start_stop_name, end_stop_name, bus_id, ticket_mode, route_id))
        mysql.connection.commit()
        ticket_id=cursor.lastrowid
        cursor.close()

        # Return success message
        return "Ticket booked successfully! Your ticket Id is " + str(ticket_id)
    else:
        # Redirect to the booking form for GET requests
        return render_template('book_ticket.html')

from datetime import datetime, timedelta

from datetime import datetime, timedelta

@app.route('/find_bus', methods=['POST', 'GET'])
def find_bus():
    if request.method == 'POST':
        # Collect user inputs
        start_stop = request.form['startStop'].strip()  # Remove extra spaces
        end_stop = request.form['endStop'].strip()

        # SQL query to find routes containing the stops in correct order
        cursor = mysql.connection.cursor(cursorclass=DictCursor)  # Dictionary output
        query = """
            SELECT DISTINCT r1.RouteID
            FROM routestops r1
            JOIN routestops r2 ON r1.RouteID = r2.RouteID
            WHERE r1.StopID = (SELECT StopID FROM stops WHERE LOWER(StopName) = %s)
              AND r2.StopID = (SELECT StopID FROM stops WHERE LOWER(StopName) = %s)
              AND r1.StopSequence < r2.StopSequence
        """
        cursor.execute(query, (start_stop.lower(), end_stop.lower()))
        routes = cursor.fetchall()

        if not routes:
            return "No routes found for the given stops."

        buses_data = []

        # Find buses and generate timings for each route
        for route in routes:
            route_id = route['RouteID']

            # Query buses for the route
            bus_query = """
                SELECT BusID, FirstBus, LastBus, FrequencyInMinutes
                FROM bus
                WHERE RouteID = %s
            """
            cursor.execute(bus_query, (route_id,))
            buses = cursor.fetchall()

            for bus in buses:
                first_bus = bus['FirstBus']
                last_bus = bus['LastBus']
                frequency = bus['FrequencyInMinutes']
                timings = []

                # Convert `first_bus` and `last_bus` to `datetime` objects for calculation
                current_time = datetime.strptime(str(first_bus), "%H:%M:%S")
                end_time = datetime.strptime(str(last_bus), "%H:%M:%S")

                # Generate timings between FirstBus and LastBus
                while current_time <= end_time:
                    timings.append(current_time.strftime("%H:%M"))
                    current_time += timedelta(minutes=frequency)

                buses_data.append({
                    'BusID': bus['BusID'],
                    'RouteID': route_id,
                    'Timings': timings
                })

        cursor.close()

        # Render results
        return render_template('find_bus_results.html', buses=buses_data)
    else:
        # Render the form for GET requests
        return render_template('find_bus.html')

@app.route('/check_ticket', methods=['GET', 'POST'])
def check_ticket():
    if request.method == 'POST':
        ticket_id = request.form['ticketID']
        
        # Create a cursor
        cursor = mysql.connection.cursor(cursorclass=DictCursor)  # Dictionary output
        
        # Fetch ticket details
        query_ticket = """
            SELECT t.*, b.journeyStatus
            FROM tickets t
            JOIN bus b ON t.busID = b.BusID
            WHERE t.TicketID = %s
        """
        cursor.execute(query_ticket, (ticket_id,))
        ticket_details = cursor.fetchone()
        
        cursor.close()
        
        if ticket_details:
            return render_template('check_ticket.html', ticket_details=ticket_details)
        else:
            error = "No ticket found with the given Ticket ID."
            return render_template('check_ticket.html', error=error)
    
    return render_template('check_ticket.html')  # For the initial GET request

@app.route('/give_feedback', methods=['GET', 'POST'])
def give_feedback():
    if request.method == 'POST':
        # Get feedback details from the form
        ticket_id = request.form['ticketID']
        bus_id = request.form['busID']
        service_feedback = request.form['serviceFeedback']
        overall_feedback = request.form['overallFeedback']
        rating = request.form['rating']
        passenger_name = request.form['passengerName']
        contact_number = request.form.get('contactNumber', None)  # Optional field

        # Insert feedback into the MaintenanceRecords table
        cursor = mysql.connection.cursor()
        cursor.execute(''' 
            INSERT INTO Feedback (TicketID, BusId, ServiceFeedback, OverallFeedback, rating_out_of_5, passengerName, contactNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (ticket_id, bus_id, service_feedback, overall_feedback, rating, passenger_name, contact_number))
        
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('passenger'))  # Redirect back to passenger options
    
    return render_template('give_feedback.html')

# Login route (for testing purpose)
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO info_table (name, age) VALUES (%s, %s)', (name, age))
        mysql.connection.commit()
        cursor.close()
        return "Done!"

app.run(host='localhost', port=5000, debug=True)