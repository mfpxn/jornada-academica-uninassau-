(() => {
  const todos = document.getElementById('selecionar-todos');
  if (!todos) return;
  todos.addEventListener('change', () => {
    document.querySelectorAll('.aluno-checkbox:not(:disabled)').forEach(caixa => {
      caixa.checked = todos.checked;
    });
  });
})();
