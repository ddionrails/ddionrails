import { createRoot } from 'react-dom/client';

function Search() {
  return <h1>SEARCH</h1>;
}

const domNode = document.getElementById('app');
const root = createRoot(domNode);
root.render(<Search />);
