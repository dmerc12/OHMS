import Table from '../components/reusable/Table';
import Page from '../components/reusable/Page';

function Material() {

    const fields = [
        {name: 'name', label: 'Material Name', type: 'text', required: true, maxLength: 255, minLength: 2},
        {name: 'description', label: 'Material Description', type: 'text', required: false, maxLength: 500, minLength: 0},
        {name: 'size', label: 'Material Size', type: 'text', required: true, maxLength: 255, minLength: 2}
    ];

    const extraFields = [
        {name: 'unit_cost', label: 'Unit Cost'},
        {name: 'available_quantity', label: 'Available Quantity'}
    ];

    return (
        <Page>
            <h1 className="h3 mb-2 text-gray-800 text-center">Materials</h1>
            <p className="mb-4 text-center">
                Materials are used in both work orders and purchases.
                They must be created here before being added to a work order or purchase.
            </p>
            <Table fields={fields} name='Material' route='/material/' extraFields={extraFields} />
        </Page>
    )
}

export default Material;