import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'duration',
})
export class DurationPipe implements PipeTransform {
  transform(value: number): string {
    if (!value) {
      return '';
    }

    if (value < 1) {
      return Math.floor(value * 1000) + ' ms';
    }

    return value.toFixed(2) + ' sek';
  }
}
