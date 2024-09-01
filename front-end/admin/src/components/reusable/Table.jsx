import { useState, useEffect, useCallback } from 'react';
import CreateModal from './CreateModal';
import UpdateModal from './UpdateModal';
import DeleteModal from './DeleteModal';
import PropTypes from 'prop-types';
import Loading from './Loading';
import api from '../../api';
import $ from 'jquery';

import 'datatables.net-bs4';
import 'datatables.net-bs4/css/dataTables.bootstrap4.min.css'

function Table({ name, fields, route }) {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const response = await api.get(route);
            setData(response.data || []);
        } catch {
            setData([]);
        } finally {
            setLoading(false);
        }
    }, [route]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    useEffect(() => {
        if (Array.isArray(data) && data.length > 0) {
            setTimeout(() => {
                $('#dataTable').DataTable();
            }, 1);
        }
    }, [data]);

    return (
        <div>
            <div className="card shadow mb-4">
                <div className="card-header py-3 d-flex justify-content-between align-items-center">
                    <h6 className="m-0 font-weight-bold text-primary">{name}s</h6>
                    <CreateModal name={name} fields={fields} route={route} fetchData={fetchData}/>
                </div>
                <div className="card-body">
                    {loading ? <Loading /> : (
                        <div className="table-responsive">
                            <table className="table table-bordered m-4" id="dataTable" width="95%" cellSpacing="0">
                                <thead>
                                    <tr>
                                        {fields.map((field, index) => (
                                            <th key={`${field.name}-${index}-header`} className='text-center'>{field.name.charAt(0).toUpperCase() + field.name.slice(1)}</th>
                                        ))}
                                        <th className='text-center'>Edit</th>
                                        <th className='text-center'>Delete</th>
                                    </tr>
                                </thead>
                                <tfoot>
                                    <tr className='text-center'>
                                        {fields.map((field, index) => (
                                            <th key={`${field.name}-${index}-footer`}>{field.name.charAt(0).toUpperCase() + field.name.slice(1)}</th>
                                        ))}
                                        <th className='text-center'>Edit</th>
                                        <th className='text-center'>Delete</th>
                                    </tr>
                                </tfoot>
                                <tbody>
                                    {Array.isArray(data) && data.length > 0 ? (
                                        data.map((item) => (
                                            <tr className="text-center" key={`${item.pk}-${item.name}`}>
                                                {fields.map((field, index) => (
                                                    <td key={`${field.name}-${index}-${item.pk}`}>{item[field.name]}</td>
                                                ))}
                                                <td key={`edit-${item.id}`}><UpdateModal name={name} fields={fields} route={route} id={item.id} fetchData={fetchData} /></td>
                                                <td key={`delete-${item.id}`}><DeleteModal name={name} route={route} id={item.id} fetchData={fetchData} /></td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr className="text-center">
                                            <td className="text-center" colSpan={fields.length + 2}>No Data Yet</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

Table.propTypes = {
    name: PropTypes.string.isRequired,
    fields: PropTypes.array.isRequired,
    route: PropTypes.string.isRequired,
}

export default Table;