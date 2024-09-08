import { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { createRoot } from 'react-dom/client';
import Loading from './Loading';
import SubForm from './SubForm';
import api from '../../api';

function FormSet({ entity, fields, route }) {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const response = await api.get(route);
            setData(response.data || [])
        } catch {
            setData([]);
        } finally {
            setLoading(false);
        }
    }, [route]);

    useEffect(() => {
        fetchData
    }, [fetchData]);

    const addSubForm = () => {
        const list = document.getElementById(`${entity}-list`);
        const newFormWrapper = document.createElement('div');
        list.appendChild(newFormWrapper);
        const root = createRoot(newFormWrapper);
        root.render(<SubForm fields={fields} route={route} isNew={true} fetchData={fetchData} />);
    }

    return (
        <div id={`${entity}-formset`}>
            <div id={`${entity}-list`}>
                <h3 className="text-center m-2">{entity}s</h3>
                {loading ? <Loading /> : (
                    Array.isArray(data) && data.length > 0 ? (
                        data.map((item, index) => (
                            <SubForm key={`${index}-${item.pk}-form`} fields={fields} route={route} isNew={false} fetchData={fetchData} initialData={item} />
                        ))
                    ) : (
                        <p className="text-center">No {entity}s Yet</p>
                    )
                )}
            </div>
            <div className='d-flex justify-content-center mt-3'>
                <button className='btn btn-success text-center' onClick={addSubForm}>Add</button>
            </div>
        </div>
    )
}

FormSet.propTypes = {
    entity: PropTypes.string.isRequired,
    route: PropTypes.string.isRequired,
    fields: PropTypes.arrayOf(
        PropTypes.shape({
            name: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
            type: PropTypes.string.isRequired,
            required: PropTypes.bool.isRequired,
            elementType: PropTypes.string.isRequired,
            maxLength: PropTypes.number,
            minLength: PropTypes.number,
            accept: PropTypes.string,
            multiple: PropTypes.bool,
            data: PropTypes.arrayOf(PropTypes.shape({
                value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
                label: PropTypes.string.isRequired
            })),
        })
    ).isRequired,
}

export default FormSet;