from django import forms

from .models import Recipe, Follow


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        text = cleaned_data.get('text')
        cooking_time = cleaned_data.get('cooking_time')
        image = cleaned_data.get('image')
        tags = cleaned_data.get('tags')

        fields = [name, text, cooking_time, image, tags]
        if not all(field for field in fields):
            raise forms.ValidationError('Не все поля рецепта заполненны')

        return cleaned_data


class RecipeIngredientInLineFormSet(forms.models.BaseInlineFormSet):

    def clean(self):
        count = 0
        ingredients = []
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
                    ingredients.append(form.cleaned_data['ingredient'])
                if form.cleaned_data['DELETE']:
                    count -= 1
                if len(ingredients) != len(set(ingredients)):
                    raise forms.ValidationError(
                        'В этом рецепте уже есть этот ингредиент')
            except (AttributeError, KeyError):
                pass
        if count < 1:
            raise forms.ValidationError('Нужен хотя бы один ингредиент')


class FollowForm(forms.ModelForm):

    class Meta:
        model = Follow
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('author') == cleaned_data.get('user'):
            raise forms.ValidationError('Нельзя подписываться на самого себя')
