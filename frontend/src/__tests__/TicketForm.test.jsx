import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TicketForm from '../components/TicketForm';

describe('TicketForm', () => {
  it('disables submit until a description is entered, then submits the input', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    render(<TicketForm onSubmit={onSubmit} />);

    const submit = screen.getByRole('button', { name: /submit ticket/i });
    expect(submit).toBeDisabled();

    await user.type(screen.getByLabelText('description'), 'My laptop will not boot');
    expect(submit).toBeEnabled();

    await user.click(submit);
    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ description: 'My laptop will not boot' }),
    );
  });

  it('shows "Submitting…" and stays disabled while submitting', () => {
    render(<TicketForm onSubmit={jest.fn()} submitting />);
    expect(screen.getByRole('button', { name: /submitting/i })).toBeDisabled();
  });
});
