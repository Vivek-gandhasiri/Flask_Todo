// app.js

// Wait until the entire page is loaded
window.onload = function() {
    fetchTasks(); // Fetch tasks on page load

    function fetchTasks() {
        $.ajax({
            type: 'GET',
            url: '/tasks', // Replace with your actual endpoint
            success: function(response) {
                console.log('Tasks received:', response); // Check what is received

                try {
                    var tasks = JSON.parse(response); // Parse JSON response

                    if (!Array.isArray(tasks)) {
                        throw new Error('Expected an array of tasks');
                    }

                    renderTasks(tasks); // Render tasks in the table
                } catch (error) {
                    console.error('Error parsing tasks:', error);
                    alert('Error parsing tasks. Please try again.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching tasks:', error);
                alert('Error fetching tasks. Please try again.');
            }
        });
    }

    function renderTasks(tasks) {
        var tasksList = $('#tasks-list');
        tasksList.empty(); // Clear previous tasks

        tasks.forEach(function(task) {
            var statusClass = getStatusClass(task.completion_status);
            var taskItem = `
                <tr>
                    <td>${task.taskname}</td>
                    <td>${task.duration}</td>
                    <td>${task.deadline}</td>
                    <td>${task.type_of_work}</td>
                    <td>${task.degree_of_importance}</td>
                    <td>
                        <select class="status-select ${statusClass}" data-task-id="${task._id}" onchange="updateTaskStatus(this)">
                            <option value="Pending" ${task.completion_status === 'Pending' ? 'selected' : ''}>Pending</option>
                            <option value="Partially Completed" ${task.completion_status === 'Partially Completed' ? 'selected' : ''}>Partially Completed</option>
                            <option value="Completed" ${task.completion_status === 'Completed' ? 'selected' : ''}>Completed</option>
                        </select>
                    </td>
                    <td><button class="delete-btn" onclick="deleteTask('${task._id}')">&#128465;</button></td>
                </tr>
            `;
            tasksList.append(taskItem);
        });
    }

    function updateTaskStatus(selectElement) {
        var taskId = $(selectElement).data('task-id');
        var newStatus = $(selectElement).val();
        $.ajax({
            type: 'PUT',
            url: '/tasks/' + taskId, // Replace with your actual endpoint
            contentType: 'application/json',
            data: JSON.stringify({ completion_status: newStatus }),
            success: function(response) {
                console.log('Task status updated:', response);
                fetchTasks(); // Refresh task list after status update
            },
            error: function(error) {
                console.error('Error updating task status:', error);
                alert('Error updating task status. Please try again.');
            }
        });
    }

    function deleteTask(taskId) {
        if (confirm('Are you sure you want to delete this task?')) {
            $.ajax({
                type: 'DELETE',
                url: '/tasks/' + taskId, // Replace with your actual endpoint
                success: function(response) {
                    console.log('Task deleted:', response);
                    fetchTasks(); // Refresh task list after deletion
                },
                error: function(error) {
                    console.error('Error deleting task:', error);
                    alert('Error deleting task. Please try again.');
                }
            });
        }
    }

    function getStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'completed':
                return 'status-completed';
            case 'partially completed':
                return 'status-partial';
            case 'pending':
                return 'status-pending';
            default:
                return '';
        }
    }
};
