from flask import Flask, request, render_template
from canvasapi import Canvas
from flask_weasyprint import HTML, CSS, render_pdf 

app = Flask(__name__) #create the Flask app

@app.route('/')
def index():
    # Displays the index page accessible at '/'
    return render_template('index.html')

@app.route('/course_manual', methods=['POST'])
def render_canvas_pdf():
    if request.method == 'POST':
        access_token = request.form['access_token']
        course_number = request.form['course_number']    
        canvas_url = request.form['canvas_url']
        # Canvas API URL
        API_URL = canvas_url
        # Canvas API key
        API_KEY = access_token

        # Initialize a new Canvas object
        canvas = Canvas(API_URL, API_KEY)

        try:
            course = canvas.get_course(course_number, include='syllabus_body')
        except Exception as e:
            message = str(e.args[0]['errors'][0]['message'])
            if 'user not authorised to perform that action' in message:
                message = 'User not authorised to perform that action. Did you spell the course code correctly?'
            return render_template('error.html', message=message)            
            
        def getmodulehtml(module, module_id):
            m = module.get_module_item(module_id)

            if m.type == "SubHeader":
                d = dict();
                d['toc'] = '<b><a href="#' + str(module_id) + '">' + m.title + '</a></b>'
                d['title'] = m.title
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>' + m.title + '</h2><p style="page-break-before: always" ></p>'
                return d
            elif m.type == "Assignment":
                assignment = course.get_assignment(m.content_id)
                d = dict();
                d['toc'] = '&bull;<a href="#' + str(module_id) + '">Assignment: ' + assignment.name + '</a>'
                d['title'] = assignment.name
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>Assignment: ' + assignment.name + '</h2><br/>' + assignment.description + '<p style="page-break-before: always" ></p>'
                return d
            elif m.type == "Quiz":
                quiz = course.get_quiz(m.content_id)
                d = dict();
                d['toc'] = '&bull;<a href="#' + str(module_id) + '">Quiz: ' + quiz.title + '</a>'
                d['title'] = quiz.title
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>Quiz: ' + quiz.title + '</h2><br/>' + quiz.description + '<br/><a href=' + quiz.mobile_url + '>Link</a><p style="page-break-before: always" ></p>'
                return d
            elif m.type == "Page":
                page = course.get_page(m.page_url)
                d = dict();
                d['toc'] = '&bull;<a href="#' + str(module_id) + '">Page: ' + page.title + '</a>'
                d['title'] = page.title
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>Page: ' + page.title + '</h2><br/>' + page.body + '<p style="page-break-before: always" ></p>'
                return d
            elif m.type == "Discussion":
                discussion = course.get_discussion_topic(i.content_id)
                d = dict();
                d['toc'] = '&bull;<a href="#' + str(module_id) + '">Discussion: ' + discussion.title + '</a>'
                d['title'] = discussion.title
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>Discussion: ' + discussion.title + '</h2><br/>' + discussion.message + '<p style="page-break-before: always" ></p>'
                return d 
            elif m.type == "File":
                d = dict();
                d['toc'] = '&bull;<a href="#' + str(module_id) + '">File: ' + m.title + '</a>'
                d['title'] = m.title
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>File: ' + m.title + '</h2><br/><a href="' + m.html_url + '">' + m.title + '</a><p style="page-break-before: always" ></p>'
                return d 
            elif m.type == "ExternalUrl":
                d = dict();
                d['toc'] = '&bull;<a href="#' + str(module_id) + '">External url: ' + m.title + '</a>'
                d['title'] = m.title
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>External url: ' + m.title + '</h2><br/><a href="' + m.external_url + '">' + m.title + '</a><p style="page-break-before: always" ></p>'
                return d
            elif m.type == "ExternalTool":
                d = dict();
                d['toc'] = '&bull;<a href="#' + str(module_id) + '">External tool: ' + m.title + '</a>'
                d['title'] = m.title
                d['html'] = '<a id="' + str(module_id) + '"></a><h2>External tool: ' + m.title + '</h2><br/><a href="' + m.html_url + '">' + m.title + '</a><p style="page-break-before: always" ></p>'
                return d

        ### CREATE HTML ###
        course_manual_html='''
        <html><head><title>''' + course.name + '''</title></head><body>
        <p>&nbsp;</p>
        <span class="a"><h1>Course Manual</h1><br/>
        <h2>''' + course.name + ''' (''' + course.course_code + ''')</h2></span>
        '''

        type_list = ['teacher']
        users = course.get_users(enrollment_type=type_list)
        type_list2 =['ta']
        users2 = course.get_users(enrollment_type=type_list2)

        course_manual_html+='<span class="b">'
        for user in users:
            course_manual_html+='<p>Teacher: ' + user.name + '</p>'
        for user2 in users2:
            course_manual_html+='<p>Teaching assistant: ' + user2.name + '</p>'
        course_manual_html+='</span><p style="page-break-before: always" ></p>' # add page break


        course_manual_html+="<h1>Table of Contents</h1><br/>"

        toc_html='<br/><h3><a href="#syllabus">Syllabus</a></h3><br/>'
        content_html=""

        modules = course.get_modules()
        for m in modules:
            module = course.get_module(m.id)
            module_items = module.get_module_items()
            toc_html+='<a href="#' + str(m.id) + '"><h3>' + module.name + '</h3></a><br/>'
            content_html+='<a id="' + str(m.id) + '"></a><h1>' + module.name + '</h1><p style="page-break-before: always" ></p>'
            for i in module_items:
                r = getmodulehtml(module, i.id)
                toc_html += r['toc'] + "<br/>"
                content_html += r['html']
        course_manual_html += toc_html + '</ul><p style="page-break-before: always" ></p>'
        course_manual_html += '<a id="syllabus"></a><h1>Syllabus</h1><br/>' + course.syllabus_body + '<p style="page-break-before: always" ></p>' + content_html        
        course_manual_html+="</body></html>"

        ### CREATE CSS ###

        css = '''

span.a {
                display: block;
                position: absolute;
                left: 100px;
                top: 100px;
            }
            span.b {
                display: block;
                position: absolute;
                left: 100px;
                top: 750px;
            }         
                  
            
            html{font-family:Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;font-size:100%;
            }
            img {
                width: auto;
                max-width: 100%;
                height: auto;
            }
            @page {
            @bottom-center{
                width: 30%;
                content: "Page " counter(page) " of " counter(pages);
            }
            @top-center {
                content: "Course Manual ''' + course.name + '''";
            }
        }
        '''
        cn = course.name
        file_name = cn.replace(" ", "_") + '.pdf'

        stylesheet = CSS(string=css)
        return render_pdf(HTML(string=course_manual_html), stylesheets=[stylesheet], download_filename=file_name)

if __name__ == '__main__':
    app.run()
