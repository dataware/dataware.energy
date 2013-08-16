<table class="table table-bordered">
            <thead>
                <tr>
                    <th>ts</th>
                    <th>sensorid</th>
                    <th>watts</th>
                </tr>
            </thead>
            <tbody>
                %for item in data:
                <tr>
                    <td>{{item['ts']}}</td>
                    <td>{{item['sensorid']}}</td>
                    <td>{{item['watts']}}</td>
                </tr>
                %end
            </tbody>
        </table>  
