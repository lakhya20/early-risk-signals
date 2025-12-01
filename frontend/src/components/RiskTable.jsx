const sample = [
  { id: '123', name: 'Alex Chen', score: 0.42, level: 'medium' },
  { id: '456', name: 'Maria Patel', score: 0.81, level: 'high' },
];

const RiskTable = () => (
  <table className="table">
    <thead>
      <tr>
        <th>Customer</th>
        <th>Score</th>
        <th>Level</th>
      </tr>
    </thead>
    <tbody>
      {sample.map((row) => (
        <tr key={row.id}>
          <td>{row.name}</td>
          <td>{row.score}</td>
          <td>{row.level}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

export default RiskTable;
