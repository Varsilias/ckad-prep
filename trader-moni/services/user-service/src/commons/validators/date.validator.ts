import {
  ValidatorConstraintInterface,
  ValidatorConstraint,
  ValidationArguments,
} from 'class-validator';
import * as dayjs from 'dayjs';

@ValidatorConstraint({ name: 'IsDateBefore', async: false })
export class IsDateBeforeConstraint implements ValidatorConstraintInterface {
  validate(start_date: any, args: ValidationArguments) {
    const object = args.object as any;
    return dayjs(start_date).isBefore(dayjs(object.end_date));
  }

  defaultMessage(args: ValidationArguments) {
    return 'Start date must be before end date.';
  }
}

@ValidatorConstraint({ name: 'IsDateAfter', async: false })
export class IsDateAfterConstraint implements ValidatorConstraintInterface {
  validate(end_date: any, args: ValidationArguments) {
    const object = args.object as any;
    return dayjs(end_date).isAfter(dayjs(object.start_date));
  }

  defaultMessage(args: ValidationArguments) {
    return `End date must be after start date.`;
  }
}
