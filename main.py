from application import create_app

app = create_app()

@app.route('/main')
def main():
    return 'Hello world'

# with app.app_context():
#     db.create_all()

# @app.route('/', methods=['POST', 'GET'])
# def index():
#     if request.method == 'POST':
#         task_content = request.form['content'] 
#         new_task = Todo(content=task_content)

#         try:
#             db.session.add(new_task)
#             db.session.commit()
#             return redirect('/')
#         except: 
#             return "There was an error adding your taks"

#     else:
#         tasks = Todo.query.order_by(Todo.date_created).all()
#         return render_template('index.html', tasks=tasks)


# @app.route('/delete/<int:id>')
# def delete(id):
#     task_to_delete = Todo.query.get_or_404(id)

#     try:
#         db.session.delete(task_to_delete)
#         db.session.commit()
#         return redirect('/')
#     except:
#         return "There was an error deleting your task"
    

# @app.route('/update/<int:id>', methods=['POST', 'GET'])
# def update(id):
#     task_to_update = Todo.query.get_or_404(id)

#     if request.method == 'POST':
#         task_to_update.content = request.form['content']
#         try:
#             db.session.commit()
#             return redirect('/')
#         except:
#             return "There was an error updating your taks"
#     else:
#         return render_template('update.html', task=task_to_update)


if __name__ == "__main__":
    app.run(debug=True)

